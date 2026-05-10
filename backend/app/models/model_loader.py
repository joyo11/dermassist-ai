from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadedModel:
    """CNN loaded from `train.py` checkpoint format."""

    model: torch.nn.Module
    device: torch.device
    checkpoint_path: Path
    meta: dict[str, Any]


def _build_backbone(model_name: str, num_classes: int) -> nn.Module:
    """Must match `models/train.py` `build_model` head architecture."""
    import torchvision.models as models

    if model_name == "resnet50":
        m = models.resnet50(weights=None)
        in_f = m.fc.in_features
        m.fc = nn.Linear(in_f, num_classes)
        return m
    if model_name == "efficientnet_b0":
        m = models.efficientnet_b0(weights=None)
        in_f = m.classifier[1].in_features
        m.classifier[1] = nn.Linear(in_f, num_classes)
        return m
    raise ValueError(f"Unsupported model_name: {model_name}. Use resnet50 or efficientnet_b0.")


def _infer_arch_from_state_dict(sd: dict[str, torch.Tensor]) -> tuple[str, int]:
    if "fc.weight" in sd:
        return "resnet50", int(sd["fc.weight"].shape[0])
    if "classifier.1.weight" in sd:
        return "efficientnet_b0", int(sd["classifier.1.weight"].shape[0])
    raise ValueError("Cannot infer architecture from state_dict (missing fc or classifier.1).")


def load_model_from_checkpoint(checkpoint_path: Path, device: Optional[torch.device] = None) -> LoadedModel:
    """
    Load weights produced by `dermassist-ai/models/train.py`.

    Expects a dict with `model_state_dict` and optional `meta` (model_name, num_classes, class_names, …).
    """
    path = checkpoint_path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {path}")

    if device is None:
        if torch.cuda.is_available():
            selected = torch.device("cuda")
        elif torch.backends.mps.is_available():
            selected = torch.device("mps")
        else:
            selected = torch.device("cpu")
    else:
        selected = device
    try:
        ckpt = torch.load(path, map_location=selected, weights_only=False)
    except TypeError:
        ckpt = torch.load(path, map_location=selected)

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
        meta = dict(ckpt.get("meta") or {})
    else:
        raise ValueError("Checkpoint must be a dict with key 'model_state_dict' (train.py format).")

    model_name = str(meta.get("model_name") or "")
    num_classes = meta.get("num_classes")

    if not model_name or num_classes is None:
        inferred_name, inferred_n = _infer_arch_from_state_dict(state)
        model_name = model_name or inferred_name
        num_classes = int(num_classes) if num_classes is not None else inferred_n

    model = _build_backbone(model_name, int(num_classes))
    model.load_state_dict(state, strict=True)
    model.to(selected)
    model.eval()

    if "class_names" not in meta and int(num_classes) == 2:
        meta["class_names"] = ["Benign", "Potentially Malignant"]
    meta.setdefault("model_name", model_name)
    meta.setdefault("num_classes", int(num_classes))

    return LoadedModel(model=model, device=selected, checkpoint_path=path, meta=meta)


# Lazy cache: None = not tried, False = failed / no path, LoadedModel = success
_load_cache: LoadedModel | bool | None = None


def get_loaded_model() -> Optional[LoadedModel]:
    """
    Load once from env `DERMASSIST_CHECKPOINT` (path to .pt file).
    Returns None if unset, missing file, or load error (app uses placeholder inference).
    """
    global _load_cache
    if isinstance(_load_cache, LoadedModel):
        return _load_cache
    if _load_cache is False:
        return None

    raw = os.environ.get("DERMASSIST_CHECKPOINT", "").strip()
    if not raw:
        _load_cache = False
        return None

    try:
        loaded = load_model_from_checkpoint(Path(raw))
        _load_cache = loaded
        logger.info("Loaded DERMASSIST_CHECKPOINT: %s", loaded.checkpoint_path)
        return loaded
    except Exception as e:
        logger.warning("DERMASSIST_CHECKPOINT load failed (%s): %s", raw, e)
        _load_cache = False
        return None


def reset_model_cache() -> None:
    """For tests or reloading after env change."""
    global _load_cache
    _load_cache = None
