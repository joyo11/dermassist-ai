# Model checkpoints

PyTorch checkpoint files (`*.pt`) are **not committed** to this repository (size and GitHub limits).

After training with [`models/train.py`](../train.py), weights are saved here, for example:

| File | Description |
|------|-------------|
| `best_binary_efficientnet_b0_fold0.pt` | Recommended binary classifier (EfficientNet-B0, fold 0). |
| `best_binary_resnet50_fold0.pt` | Binary ResNet-50 comparison run. |

## Obtain weights

1. **Train locally** — Follow [Training](../../README.md#training-ham10000-pytorch) in the root README using HAM10000 under `archive/` (download separately).
2. **GitHub Release** — If the maintainer publishes artifacts, download release `.pt` files into this folder.

Set `DERMASSIST_CHECKPOINT` to the absolute or relative path of your `.pt` file (see `backend/README.md`).

Small JSON sidecars (`metrics_*.json`, `model_meta_*.json`, `train_config_*.json`) may be tracked for reproducibility when present.
