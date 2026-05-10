#!/usr/bin/env python3
"""Print discovered HAM10000 root — no deps beyond stdlib (for pre-venv use)."""
from __future__ import annotations

import os
from pathlib import Path


def valid(p: Path) -> bool:
    p = p.expanduser().resolve()
    if not (p / "HAM10000_metadata.csv").is_file():
        return False
    for sub in ("HAM10000_images_part_1", "HAM10000_images_part_2"):
        if not (p / sub).is_dir():
            return False
    return True


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    env = os.environ.get("HAM10000_ROOT", "").strip()
    if env:
        ep = Path(env).expanduser().resolve()
        if valid(ep):
            print(ep, end="")
            return
        raise SystemExit(f"Invalid HAM10000_ROOT: {ep}")
    for c in (repo / "datasets" / "ham10000", repo / "archive"):
        if valid(c):
            print(c.resolve(), end="")
            return
    raise SystemExit(
        f"No HAM10000 found under {repo}/datasets/ham10000 or {repo}/archive"
    )


if __name__ == "__main__":
    main()
