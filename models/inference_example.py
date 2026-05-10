"""
Example script showing how a trained model might be used for inference (future work).

This is separate from the FastAPI backend to keep experimentation simple.
"""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    image_path = Path("path/to/your/image.jpg")
    checkpoint_path = Path("models/checkpoints/model.pt")

    # TODO:
    # - read image bytes
    # - preprocess to tensor (same pipeline as backend)
    # - load checkpoint
    # - run model forward pass
    # - map logits -> probabilities -> label

    print("Inference example scaffold created.")
    print(f"Image: {image_path}")
    print(f"Checkpoint: {checkpoint_path}")


if __name__ == "__main__":
    main()

