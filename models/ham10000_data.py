"""
HAM10000 helpers: metadata loading, image path resolution, label maps.

Research-only. Not for clinical use.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import pandas as pd

# Seven HAM10000 diagnosis codes in metadata column `dx`.
DX_CLASSES_7 = ("akiec", "bcc", "bkl", "df", "mel", "nv", "vasc")

# Binary grouping for DermAssist-style risk screening (research prototype).
# Document this mapping in any paper or report; it is a design choice, not ground truth pathology.
HIGH_RISK_DX = frozenset({"mel", "bcc", "akiec"})
LOW_RISK_DX = frozenset({"nv", "bkl", "df", "vasc"})

TaskMode = Literal["binary", "multiclass"]


def default_archive_dir() -> Path:
    """Deprecated: use ``discover_ham10000_root()`` for flexible layout."""
    return Path(__file__).resolve().parent.parent / "archive"


def is_valid_ham10000_root(path: Path) -> bool:
    """True if CSV and both image part folders exist."""
    p = path.expanduser().resolve()
    if not (p / "HAM10000_metadata.csv").is_file():
        return False
    for sub in ("HAM10000_images_part_1", "HAM10000_images_part_2"):
        if not (p / sub).is_dir():
            return False
    return True


def discover_ham10000_root(explicit_repo_root: Path | None = None) -> Path:
    """
    Locate HAM10000 files under the DermAssist AI repo.

    Order:
    1. Env ``HAM10000_ROOT`` if set and valid
    2. ``dermassist-ai/datasets/ham10000/``
    3. ``dermassist-ai/archive/``
    """
    repo = explicit_repo_root or Path(__file__).resolve().parent.parent

    env = os.environ.get("HAM10000_ROOT", "").strip()
    if env:
        ep = Path(env).expanduser().resolve()
        if is_valid_ham10000_root(ep):
            return ep
        raise FileNotFoundError(
            f"HAM10000_ROOT is set but invalid (need CSV + both image parts): {ep}"
        )

    for candidate in (repo / "datasets" / "ham10000", repo / "archive"):
        if is_valid_ham10000_root(candidate):
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not find HAM10000. Expected either:\n"
        f"  {repo / 'datasets' / 'ham10000'}\n"
        f"  {repo / 'archive'}\n"
        "with HAM10000_metadata.csv and HAM10000_images_part_1/ and HAM10000_images_part_2/, "
        "or set HAM10000_ROOT to that folder."
    )


def build_image_lookup(archive_dir: Path) -> dict[str, Path]:
    """Map `image_id` (stem, e.g. ISIC_0027419) -> absolute path to .jpg."""
    lookup: dict[str, Path] = {}
    for sub in ("HAM10000_images_part_1", "HAM10000_images_part_2"):
        folder = archive_dir / sub
        if not folder.is_dir():
            continue
        for p in folder.glob("*.jpg"):
            lookup[p.stem] = p.resolve()
    return lookup


def load_metadata_csv(archive_dir: Path) -> pd.DataFrame:
    csv_path = archive_dir / "HAM10000_metadata.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"Missing metadata CSV: {csv_path}")
    return pd.read_csv(csv_path)


def prepare_frame(
    archive_dir: Path,
    task: TaskMode,
) -> pd.DataFrame:
    """
    Returns a DataFrame with columns: lesion_id, image_id, dx, image_path, y (int label).
    Drops rows with missing files or unknown dx.
    """
    df = load_metadata_csv(archive_dir)
    lookup = build_image_lookup(archive_dir)

    df = df.copy()
    df["image_path"] = df["image_id"].astype(str).map(lambda i: lookup.get(i))
    df = df.dropna(subset=["image_path"])

    unknown_dx = ~df["dx"].isin(set(DX_CLASSES_7))
    if unknown_dx.any():
        df = df.loc[~unknown_dx]

    if task == "binary":
        def to_bin(dx: str) -> int:
            if dx in HIGH_RISK_DX:
                return 1  # Potentially Malignant (research label)
            if dx in LOW_RISK_DX:
                return 0  # Benign (research label)
            raise ValueError(dx)

        df["y"] = df["dx"].map(to_bin)
    else:
        dx_to_idx = {c: i for i, c in enumerate(DX_CLASSES_7)}
        df["y"] = df["dx"].map(dx_to_idx)

    return df.reset_index(drop=True)


def compute_class_weights(y: pd.Series, num_classes: int) -> list[float]:
    """Inverse-frequency weights (normalized) for CrossEntropyLoss weight=."""
    counts = y.value_counts().reindex(range(num_classes), fill_value=0)
    total = len(y)
    w = total / (num_classes * counts.clip(lower=1))
    w = w / w.mean()
    return [float(w[i]) for i in range(num_classes)]
