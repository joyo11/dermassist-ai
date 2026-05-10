# System Architecture

DermAssist AI is a full-stack research prototype with a web UI and a Python inference API.

## High-level flow

Frontend → FastAPI Backend → Preprocessing → PyTorch Model → Prediction Response → UI Display

## Components

### Frontend (React + Tailwind / Next.js)

- Image selection (JPG/PNG) + preview
- “Analyze Image” sends `multipart/form-data` to `POST /predict` with `file` and `include_gradcam=true`
- Displays: prediction label, risk category, confidence, explanation, disclaimer
- When the backend returns `gradcam_image_base64`, shows **Model Attention Heatmap** (Grad-CAM overlay) plus a short disclaimer that it reflects model attention, not medical evidence

### Backend (FastAPI)

- `POST /predict` accepts uploaded image files (JPG/PNG)
- Validates file type and content
- Preprocesses image (PIL → RGB → resize 224×224 → ImageNet normalize → tensor)
- Loads optional PyTorch checkpoint from env `DERMASSIST_CHECKPOINT` (binary EfficientNet-B0 or ResNet-50 from `models/train.py`)
- Runs inference; optionally runs **Grad-CAM** on the same preprocessed tensor for explainability
- Returns structured JSON (`prediction`, `risk_category`, `confidence`, `explanation`, `disclaimer`, optional `gradcam_image_base64`, `attention_heatmap_label`, `attention_heatmap_disclaimer`)

### Model / Inference (PyTorch)

- Transfer learning from ImageNet-pretrained **EfficientNet-B0** (recommended) or **ResNet-50**
- Checkpoint format: `model_state_dict` + `meta` (model name, class names, fold, etc.)
- **Grad-CAM** (`app/services/gradcam.py`): target layer is architecture-specific (EfficientNet: last MBConv `features[-2]`; ResNet-50: `layer4[-1]`). Output is a PNG heatmap encoded as standard base64 (no `data:` prefix).
