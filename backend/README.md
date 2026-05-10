# DermAssist AI Backend (FastAPI)

This backend powers the DermAssist AI research prototype. It accepts a skin lesion image and returns an **educational/research risk screening** result.

## Disclaimer

DermAssist AI is **not** a medical diagnosis tool and must never be used to diagnose cancer or any condition. Outputs are for education/research only.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Trained model (optional)

**Workflow:** train **binary ResNet50** first (`--task binary --model resnet50`), confirm the app end-to-end, then train **binary EfficientNet-B0** (`--model efficientnet_b0`) and compare with `models/evaluate.py`. **Recommended serve:** `best_binary_efficientnet_b0_fold0.pt` (better held-out ROC-AUC / F1 / fewer FN vs ResNet on fold 0 — see `docs/model_evaluation.md`).

After training with `models/train.py`, point the API at your checkpoint:

```bash
export DERMASSIST_CHECKPOINT="/absolute/path/to/dermassist-ai/models/checkpoints/best_binary_efficientnet_b0_fold0.pt"
uvicorn app.main:app --reload --port 8000
```

To run ResNet-50 instead, use `best_binary_resnet50_fold0.pt`.

If `DERMASSIST_CHECKPOINT` is unset or the file fails to load, `POST /predict` falls back to **placeholder** inference (see logs).

Copy `.env.example` to `.env` and set `DERMASSIST_CHECKPOINT` if your process manager loads env files.

## API

- `GET /health`: health check
- `POST /predict`: image upload prediction

### `POST /predict`

- **Request**: `multipart/form-data` with field name `file` (JPG or PNG). Optional field **`include_gradcam`** (default `true`): when a checkpoint is loaded, the backend may return a Grad-CAM PNG as base64.
- **Response**:

```json
{
  "prediction": "Benign",
  "risk_category": "Low Risk",
  "confidence": 0.87,
  "explanation": "…",
  "disclaimer": "This tool is for educational and research purposes only and is not a medical diagnosis.",
  "gradcam_image_base64": "<PNG bytes as standard base64, or null>",
  "attention_heatmap_label": "Model Attention Heatmap",
  "attention_heatmap_disclaimer": "This heatmap shows model attention, not medical evidence."
}
```

`gradcam_image_base64` and the attention fields are omitted or null without a valid checkpoint or when Grad-CAM fails.

## Model integration

- Set `DERMASSIST_CHECKPOINT` to a `.pt` file saved by `models/train.py` (`model_state_dict` + `meta`).
- Supported architectures in checkpoint: **ResNet50**, **EfficientNet-B0** (must match training). Grad-CAM targets the last convolutional block appropriate to each architecture.
- **Binary** checkpoints (`num_classes == 2`) map directly to API labels.
- **7-class** checkpoints are collapsed to Benign vs Potentially Malignant using the same high-risk `dx` set as training (`mel`, `bcc`, `akiec`).

