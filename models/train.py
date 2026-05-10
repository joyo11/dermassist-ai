"""
Train a CNN on HAM10000 (research prototype).

Default data layout (DermAssist AI):
  dermassist-ai/archive/
    HAM10000_metadata.csv
    HAM10000_images_part_1/*.jpg
    HAM10000_images_part_2/*.jpg

Not a medical diagnosis tool. For education/research only.

Usage (from repo root or from `models/`):
  cd dermassist-ai/models
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements-train.txt

  # 1) Recommended first: binary + ResNet50, wire backend end-to-end
  python train.py --data-root ../archive --task binary --model resnet50 --epochs 10

  # 2) Comparison / default serve (better ROC-AUC/F1 on fold 0 — see docs/model_evaluation.md)
  python train.py --data-root ../archive --task binary --model efficientnet_b0 --epochs 10

  # Optional: multiclass (7 dx)
  python train.py --data-root ../archive --task multiclass --model resnet50 --epochs 15
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from ham10000_data import (
    DX_CLASSES_7,
    TaskMode,
    compute_class_weights,
    discover_ham10000_root,
    prepare_frame,
)


def _configure_ssl_for_pretrained_downloads() -> None:
    """
    macOS (and some Python.org builds) often hit SSL verify errors when torchvision
    downloads ImageNet weights from download.pytorch.org. Point SSL at certifi's CA bundle.
    """
    import os
    import ssl

    try:
        import certifi
    except ImportError:
        return
    ca = certifi.where()
    os.environ.setdefault("SSL_CERT_FILE", ca)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", ca)
    try:

        def _https_context() -> ssl.SSLContext:
            return ssl.create_default_context(cafile=ca)

        ssl._create_default_https_context = _https_context  # type: ignore[misc, assignment]
    except Exception:
        pass


# Reproducibility
def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class Ham10000ImageDataset(Dataset):
    def __init__(
        self,
        frame: pd.DataFrame,
        image_size: int,
        is_training: bool,
    ) -> None:
        self.paths = frame["image_path"].tolist()
        self.labels = frame["y"].astype(np.int64).tolist()
        self.image_size = image_size
        self.is_training = is_training

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        path = Path(self.paths[idx])
        y = self.labels[idx]
        img = Image.open(path).convert("RGB")
        if self.is_training:
            # Light augmentation suitable for dermoscopy
            img = torchvision_transforms_train(img, self.image_size)
        else:
            img = torchvision_transforms_eval(img, self.image_size)
        return img, y


def torchvision_transforms_train(img: Image.Image, size: int) -> torch.Tensor:
    import torchvision.transforms as T

    transform = T.Compose(
        [
            T.Resize((size, size)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.5),
            T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.05, hue=0.02),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return transform(img)


def torchvision_transforms_eval(img: Image.Image, size: int) -> torch.Tensor:
    import torchvision.transforms as T

    transform = T.Compose(
        [
            T.Resize((size, size)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return transform(img)


def build_model(model_name: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    import torchvision.models as models

    weights = "DEFAULT" if pretrained else None
    try:
        if model_name == "resnet50":
            m = models.resnet50(weights=weights)
            in_f = m.fc.in_features
            m.fc = nn.Linear(in_f, num_classes)
            return m
        if model_name == "efficientnet_b0":
            m = models.efficientnet_b0(weights=weights)
            in_f = m.classifier[1].in_features
            m.classifier[1] = nn.Linear(in_f, num_classes)
            return m
    except Exception as e:
        if pretrained:
            print(
                f"WARNING: Could not load ImageNet pretrained weights ({e}); "
                "training from randomly initialized backbone."
            )
            return build_model(model_name, num_classes, pretrained=False)
        raise
    raise ValueError(f"Unknown model_name: {model_name}. Use resnet50 or efficientnet_b0.")


@dataclass
class TrainConfig:
    archive_dir: Path
    output_dir: Path
    task: TaskMode
    model_name: str
    image_size: int
    batch_size: int
    num_epochs: int
    lr: float
    weight_decay: float
    num_workers: int
    seed: int
    fold: int  # which StratifiedGroupKFold split (0..n_splits-1)


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> float:
    model.train()
    total_loss = 0.0
    n = 0
    for x, y in tqdm(loader, desc="train", leave=False):
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        n += x.size(0)
    return total_loss / max(n, 1)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    num_classes: int,
) -> tuple[float, float]:
    model.eval()
    total_loss = 0.0
    n = 0
    correct = 0
    for x, y in tqdm(loader, desc="val", leave=False):
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        logits = model(x)
        loss = criterion(logits, y)
        total_loss += loss.item() * x.size(0)
        n += x.size(0)
        pred = logits.argmax(dim=1)
        correct += (pred == y).sum().item()
    acc = correct / max(n, 1)
    return total_loss / max(n, 1), acc


def main() -> None:
    _configure_ssl_for_pretrained_downloads()

    parser = argparse.ArgumentParser(description="Train HAM10000 classifier (research).")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Folder with HAM10000_metadata.csv + image parts (default: auto-discover datasets/ham10000 or archive)",
    )
    parser.add_argument("--output-dir", type=Path, default=None, help="Checkpoints (default: models/checkpoints)")
    parser.add_argument("--task", choices=["binary", "multiclass"], default="binary")
    parser.add_argument("--model", choices=["resnet50", "efficientnet_b0"], default="resnet50")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fold", type=int, default=0, help="StratifiedGroupKFold fold index (0-4)")
    parser.add_argument("--n-splits", type=int, default=5)
    args = parser.parse_args()

    repo_models = Path(__file__).resolve().parent
    archive_dir = (
        args.data_root.expanduser().resolve() if args.data_root else discover_ham10000_root()
    )
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else (repo_models / "checkpoints")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    set_seed(args.seed)
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Device: {device}")
    print(f"Archive: {archive_dir}")

    task: TaskMode = args.task  # type: ignore[assignment]
    df = prepare_frame(archive_dir, task=task)
    num_classes = 2 if task == "binary" else len(DX_CLASSES_7)
    print(f"Samples with images: {len(df)} | task={task} | num_classes={num_classes}")

    sgkf = StratifiedGroupKFold(n_splits=args.n_splits, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(df, df["y"], groups=df["lesion_id"]))
    if args.fold < 0 or args.fold >= len(splits):
        raise SystemExit(f"--fold must be in 0..{len(splits)-1}")
    train_idx, val_idx = splits[args.fold]
    train_df = df.iloc[train_idx].reset_index(drop=True)
    val_df = df.iloc[val_idx].reset_index(drop=True)
    print(f"Train: {len(train_df)} | Val: {len(val_df)} (patient-aware split)")

    train_ds = Ham10000ImageDataset(train_df, args.image_size, is_training=True)
    val_ds = Ham10000ImageDataset(val_df, args.image_size, is_training=False)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )

    model = build_model(args.model, num_classes, pretrained=True).to(device)
    weights = compute_class_weights(train_df["y"], num_classes)
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    best_val_acc = 0.0
    best_path = output_dir / f"best_{task}_{args.model}_fold{args.fold}.pt"

    class_names: list[str]
    if task == "binary":
        class_names = ["Benign", "Potentially Malignant"]
    else:
        class_names = list(DX_CLASSES_7)

    meta: dict[str, Any] = {
        "task": task,
        "model_name": args.model,
        "num_classes": num_classes,
        "class_names": class_names,
        "binary_dx_high_risk": sorted({"mel", "bcc", "akiec"}),
        "binary_dx_low_risk": sorted({"nv", "bkl", "df", "vasc"}),
        "image_size": args.image_size,
        "fold": args.fold,
        "n_splits": args.n_splits,
    }

    for epoch in range(1, args.epochs + 1):
        tr_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        va_loss, va_acc = evaluate(model, val_loader, criterion, device, num_classes)
        print(f"Epoch {epoch}/{args.epochs}  train_loss={tr_loss:.4f}  val_loss={va_loss:.4f}  val_acc={va_acc:.4f}")
        if va_acc > best_val_acc:
            best_val_acc = va_acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "meta": meta,
                    "val_acc": va_acc,
                    "epoch": epoch,
                },
                best_path,
            )
            print(f"  saved {best_path} (val_acc={va_acc:.4f})")

    # Save run config next to checkpoint
    cfg = TrainConfig(
        archive_dir=archive_dir,
        output_dir=output_dir,
        task=task,
        model_name=args.model,
        image_size=args.image_size,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        lr=args.lr,
        weight_decay=args.weight_decay,
        num_workers=args.num_workers,
        seed=args.seed,
        fold=args.fold,
    )
    tag = f"{task}_{args.model}_fold{args.fold}"
    metrics_path = output_dir / f"metrics_{tag}.json"
    with open(output_dir / f"train_config_{tag}.json", "w", encoding="utf-8") as f:
        json.dump({k: str(v) if isinstance(v, Path) else v for k, v in asdict(cfg).items()}, f, indent=2)
    with open(output_dir / f"model_meta_{tag}.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "best_val_acc": best_val_acc,
                "checkpoint": str(best_path),
                "task": task,
                "model_name": args.model,
                "fold": args.fold,
                "epochs_run": args.epochs,
            },
            f,
            indent=2,
        )

    print(f"Done. Best val acc: {best_val_acc:.4f} -> {best_path}")


if __name__ == "__main__":
    main()
