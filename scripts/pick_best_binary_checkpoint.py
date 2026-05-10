#!/usr/bin/env python3
"""Compare validation accuracy from metrics JSON; prefer ResNet50 on ties."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHK = ROOT / "models" / "checkpoints"
FOLD = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def load_acc(name: str) -> tuple[float, Path]:
    p = CHK / name
    if not p.is_file():
        return -1.0, p
    data = json.loads(p.read_text(encoding="utf-8"))
    return float(data.get("best_val_acc", -1.0)), Path(data.get("checkpoint", ""))


def main() -> None:
    r_acc, r_ckpt = load_acc(f"metrics_binary_resnet50_fold{FOLD}.json")
    e_acc, e_ckpt = load_acc(f"metrics_binary_efficientnet_b0_fold{FOLD}.json")

    if r_acc < 0 and e_acc < 0:
        print("ERROR: No metrics files found. Train first.", file=sys.stderr)
        sys.exit(1)

    # Tie or missing EfficientNet -> ResNet50 (more stable default)
    if e_acc < 0 or r_acc >= e_acc:
        chosen, label = r_ckpt, f"resnet50 (val_acc={r_acc:.4f})"
    else:
        chosen, label = e_ckpt, f"efficientnet_b0 (val_acc={e_acc:.4f})"

    if not chosen.is_file():
        print(f"ERROR: Checkpoint missing: {chosen}", file=sys.stderr)
        sys.exit(1)

    print(str(chosen.resolve()))
    print(f"# Selected: {label}; resnet_val_acc={r_acc:.4f} efficientnet_val_acc={e_acc:.4f}", file=sys.stderr)


if __name__ == "__main__":
    main()
