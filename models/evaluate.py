"""
Evaluate a DermAssist checkpoint on held-out HAM10000 validation images only.

**No training images are used for metrics.** The script builds the same
StratifiedGroupKFold split as `train.py`, takes only the validation indices for
the checkpoint's fold, and runs inference on that subset. Training rows are
computed only to assert disjointness, then discarded.

When the checkpoint `meta` includes `fold` and `n_splits`, those values are
used so the holdout set matches the one the model was not trained on.

Usage (from repo root or models/):
  pip install -r requirements-train.txt matplotlib seaborn
  python evaluate.py --checkpoint checkpoints/best_binary_resnet50_fold0.pt
  python evaluate.py --checkpoint checkpoints/best_binary_efficientnet_b0_fold0.pt --plots-dir ../docs/assets
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)
from sklearn.model_selection import StratifiedGroupKFold
from torch.utils.data import DataLoader
from tqdm import tqdm

# Allow imports when run as script
_REPO_MODELS = Path(__file__).resolve().parent
if str(_REPO_MODELS) not in sys.path:
    sys.path.insert(0, str(_REPO_MODELS))

from ham10000_data import TaskMode, discover_ham10000_root, prepare_frame  # noqa: E402
from train import Ham10000ImageDataset, build_model, set_seed, torchvision_transforms_eval  # noqa: E402


def load_checkpoint(path: Path, device: torch.device) -> tuple[nn.Module, dict[str, Any]]:
    ckpt = torch.load(path, map_location=device, weights_only=False)
    if not isinstance(ckpt, dict) or "model_state_dict" not in ckpt:
        raise ValueError("Expected train.py checkpoint with model_state_dict")
    state = ckpt["model_state_dict"]
    meta = dict(ckpt.get("meta") or {})

    model_name = str(meta.get("model_name") or "")
    num_classes = meta.get("num_classes")
    if not model_name or num_classes is None:
        if "fc.weight" in state:
            model_name = "resnet50"
            num_classes = int(state["fc.weight"].shape[0])
        elif "classifier.1.weight" in state:
            model_name = "efficientnet_b0"
            num_classes = int(state["classifier.1.weight"].shape[0])
        else:
            raise ValueError("Cannot infer architecture from checkpoint")

    model = build_model(model_name, int(num_classes), pretrained=False)
    model.load_state_dict(state, strict=True)
    model.to(device)
    model.eval()
    meta.setdefault("model_name", model_name)
    meta.setdefault("num_classes", int(num_classes))
    return model, meta


@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns y_true, y_pred, p_malignant (probability of class 1 for binary)."""
    ys: list[int] = []
    preds: list[int] = []
    probs_1: list[float] = []

    for x, y in tqdm(loader, desc="eval", leave=False):
        x = x.to(device, non_blocking=True)
        logits = model(x)
        prob = torch.softmax(logits, dim=1)
        pred = logits.argmax(dim=1)
        ys.extend(y.numpy().tolist())
        preds.extend(pred.cpu().numpy().tolist())
        if prob.shape[1] == 2:
            probs_1.extend(prob[:, 1].cpu().numpy().tolist())
        else:
            probs_1.extend(torch.max(prob, dim=1).values.cpu().numpy().tolist())

    return (
        np.array(ys, dtype=np.int64),
        np.array(preds, dtype=np.int64),
        np.array(probs_1, dtype=np.float64),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate HAM10000 checkpoint (research).")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--fold", type=int, default=0)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--plots-dir", type=Path, default=None, help="e.g. ../docs/assets")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )

    archive = (
        args.data_root.expanduser().resolve()
        if args.data_root
        else discover_ham10000_root()
    )
    ckpt_path = args.checkpoint.expanduser().resolve()
    model, meta = load_checkpoint(ckpt_path, device)
    task: TaskMode = "binary"
    df = prepare_frame(archive, task=task)

    # Match training holdout: prefer fold / n_splits stored in checkpoint meta.
    eval_n_splits = (
        int(meta["n_splits"]) if meta.get("n_splits") is not None else args.n_splits
    )
    eval_fold = int(meta["fold"]) if meta.get("fold") is not None else args.fold
    if meta.get("fold") is not None and meta.get("n_splits") is not None:
        if args.fold != eval_fold or args.n_splits != eval_n_splits:
            print(
                f"Using fold={eval_fold}, n_splits={eval_n_splits} from checkpoint meta "
                f"(not CLI --fold {args.fold} --n-splits {args.n_splits}) "
                "so validation images are the same held-out set the model never trained on.",
                file=sys.stderr,
            )

    if eval_fold < 0 or eval_fold >= eval_n_splits:
        raise SystemExit(f"--fold must be in 0..{eval_n_splits - 1} (got {eval_fold})")

    sgkf = StratifiedGroupKFold(
        n_splits=eval_n_splits, shuffle=True, random_state=args.seed
    )
    splits = list(sgkf.split(df, df["y"], groups=df["lesion_id"]))
    train_idx, val_idx = splits[eval_fold]
    train_set, val_set = set(train_idx.tolist()), set(val_idx.tolist())
    if train_set & val_set:
        raise RuntimeError("train/val index overlap; split is invalid")
    if train_set | val_set != set(range(len(df))):
        raise RuntimeError("train/val indices do not partition the dataset")

    # Metrics use validation rows only — never the training subset.
    val_df = df.iloc[val_idx].reset_index(drop=True)
    _train_n = len(train_idx)
    print(
        f"Held-out validation only: {len(val_df)} images "
        f"(fold {eval_fold}/{eval_n_splits}; {_train_n} train images excluded from metrics)",
        file=sys.stderr,
    )
    image_size = int(meta.get("image_size", 224))

    val_ds = Ham10000ImageDataset(val_df, image_size, is_training=False)
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
    )

    y_true, y_pred, p_mal = collect_predictions(model, val_loader, device)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0))
    rec = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = (int(x) for x in cm.ravel())

    try:
        roc_auc = float(roc_auc_score(y_true, p_mal))
    except ValueError:
        roc_auc = float("nan")

    results = {
        "checkpoint": str(ckpt_path),
        "model_name": meta.get("model_name"),
        "task": task,
        "fold": eval_fold,
        "n_splits": eval_n_splits,
        "evaluated_on": "held_out_validation_only",
        "train_images_excluded": _train_n,
        "val_n": int(len(y_true)),
        "accuracy": acc,
        "precision_malignant": prec,
        "recall_malignant": rec,
        "f1_malignant": f1,
        "confusion_matrix": {"labels": [0, 1], "matrix": cm.tolist()},
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "true_positives": tp,
        "roc_auc_malignant": roc_auc,
        "label_0": "Benign (research label)",
        "label_1": "Potentially Malignant (research label)",
    }

    print(json.dumps(results, indent=2))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    if args.plots_dir:
        import matplotlib.pyplot as plt
        import seaborn as sns

        args.plots_dir.mkdir(parents=True, exist_ok=True)
        tag = f"{meta.get('model_name', 'model')}_fold{eval_fold}"

        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Pred Benign", "Pred Mal."],
            yticklabels=["True Benign", "True Mal."],
            ax=ax,
        )
        ax.set_title(f"Confusion matrix ({tag})")
        fig.tight_layout()
        fig.savefig(args.plots_dir / f"confusion_matrix_{tag}.png", dpi=150)
        plt.close(fig)

        if not np.isnan(roc_auc):
            fpr, tpr, _ = roc_curve(y_true, p_mal, pos_label=1)
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
            ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
            ax.set_xlabel("False positive rate")
            ax.set_ylabel("True positive rate")
            ax.set_title(f"ROC — malignant class ({tag})")
            ax.legend(loc="lower right")
            fig.tight_layout()
            fig.savefig(args.plots_dir / f"roc_curve_{tag}.png", dpi=150)
            plt.close(fig)

            prec_curve, rec_curve, _ = precision_recall_curve(y_true, p_mal, pos_label=1)
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(rec_curve, prec_curve)
            ax.set_xlabel("Recall (malignant)")
            ax.set_ylabel("Precision (malignant)")
            ax.set_title(f"Precision–recall ({tag})")
            fig.tight_layout()
            fig.savefig(args.plots_dir / f"pr_curve_{tag}.png", dpi=150)
            plt.close(fig)


if __name__ == "__main__":
    main()
