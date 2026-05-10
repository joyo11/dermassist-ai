# DermAssist AI

**DermAssist AI** is a full-stack **research prototype** for educational skin-lesion **risk screening** using deep learning on public dermoscopy data (HAM10000). It pairs a **Next.js** frontend with a **FastAPI** backend and **PyTorch** models (EfficientNet-B0 / ResNet-50), optional **Grad-CAM** overlays, and evaluation artifacts.

---

## Disclaimer

**This is not a medical device and not a diagnostic tool.**

- Outputs are for **education and research** only.
- Do **not** use predictions to make clinical decisions or delay care.
- Always consult a qualified clinician for health concerns.

Full text: [`docs/disclaimer.md`](docs/disclaimer.md).

---

## Overview

| Layer | Role |
|--------|------|
| **Frontend** | Upload JPG/PNG, call `/predict`, show label, risk band, confidence, explanation, optional **Model Attention Heatmap** (Grad-CAM). |
| **Backend** | Image preprocessing (224×224, ImageNet normalization), PyTorch inference, optional Grad-CAM PNG as base64 in JSON. |
| **Models** | Binary screening: “Benign” vs “Potentially Malignant” (research mapping from HAM10000 diagnoses). |

Recommended serving checkpoint (held-out metrics): **EfficientNet-B0** — see [Evaluation summary](#evaluation-summary) and [`docs/model_evaluation.md`](docs/model_evaluation.md).

---

## Architecture

High-level flow: **Browser → FastAPI → preprocess → CNN → JSON → UI**.

Details: [`docs/system_architecture.md`](docs/system_architecture.md)  
Proposal / roadmap: [`docs/project_proposal.md`](docs/project_proposal.md), [`docs/research_roadmap.md`](docs/research_roadmap.md).

```
dermassist-ai/
├── frontend/          # Next.js + Tailwind UI
├── backend/           # FastAPI, inference, Grad-CAM
├── models/            # train.py, evaluate.py, checkpoints/ (weights not in git — see below)
├── docs/              # Evaluation, disclaimer, architecture, assets (plots + JSON)
├── archive/           # HAM10000 — local only (gitignored; see archive/README.md)
├── scripts/           # Optional training workflows
└── notebooks/         # Research placeholders
```

---

## Setup

### Prerequisites

- Python **3.11+**
- Node.js **18+** (for the frontend)
- HAM10000 placed under `archive/` if you train or evaluate locally ([`archive/README.md`](archive/README.md))

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `backend/.env.example` to `.env` if you use env files.

**Checkpoint (recommended — EfficientNet-B0):** weights are **not** stored in git. After training (or downloading from a release), point the API at your `.pt` file:

```bash
export DERMASSIST_CHECKPOINT="$PWD/../models/checkpoints/best_binary_efficientnet_b0_fold0.pt"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If `DERMASSIST_CHECKPOINT` is unset or invalid, `/predict` still runs using **placeholder** inference.

Health check: `GET http://127.0.0.1:8000/health`

More detail: [`backend/README.md`](backend/README.md).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL if the API is not on localhost:8000
npm run dev
```

Open the URL printed in the terminal (often `http://localhost:3000`).

---

## Training (HAM10000)

From `models/`:

```bash
cd models
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-train.txt
```

**Binary + ResNet-50** (good first wiring pass):

```bash
python train.py --data-root ../archive --task binary --model resnet50 --epochs 10 --batch-size 32
```

**Binary + EfficientNet-B0** (recommended server model after comparison):

```bash
python train.py --data-root ../archive --task binary --model efficientnet_b0 --epochs 10 --batch-size 32
```

Checkpoints are written under `models/checkpoints/` — see [`models/checkpoints/README.md`](models/checkpoints/README.md). **macOS:** `train.py` configures SSL for torchvision pretrained downloads (`certifi` in `requirements-train.txt`).

---

## Evaluation summary

Held-out validation (StratifiedGroupKFold, fold **0** / **5**, seed **42**). Full tables and plots: [`docs/model_evaluation.md`](docs/model_evaluation.md). JSON mirrors: [`docs/assets/eval_efficientnet_b0_fold0.json`](docs/assets/eval_efficientnet_b0_fold0.json), [`docs/assets/eval_resnet50_fold0.json`](docs/assets/eval_resnet50_fold0.json).

| Model | Accuracy | F1 (malignant) | ROC-AUC |
|--------|----------|----------------|---------|
| **EfficientNet-B0** (recommended) | **0.878** | **0.723** | **0.930** |
| ResNet-50 | 0.876 | 0.650 | 0.914 |

Reproduce:

```bash
cd models
pip install -r requirements-train.txt
python evaluate.py --checkpoint checkpoints/best_binary_efficientnet_b0_fold0.pt \
  --data-root ../archive --plots-dir ../docs/assets --json-out ../docs/assets/eval_efficientnet_b0_fold0.json
```

---

## Grad-CAM explainability

With a loaded checkpoint, `POST /predict` can return:

- `gradcam_image_base64` — PNG overlay (standard base64, no `data:` prefix)
- `attention_heatmap_label` — **“Model Attention Heatmap”**
- `attention_heatmap_disclaimer` — **“This heatmap shows model attention, not medical evidence.”**

Form field `include_gradcam` defaults to **true**. EfficientNet-B0 uses the last MBConv block; preprocessing matches inference. See [`docs/model_evaluation.md`](docs/model_evaluation.md) (Grad-CAM section) and [`docs/system_architecture.md`](docs/system_architecture.md).

---

## Screenshots & demo

Place screenshots under [`docs/screenshots/`](docs/screenshots/) (see [`docs/screenshots/README.md`](docs/screenshots/README.md)). Suggested captures:

1. Upload + analyze flow  
2. Results with **Model Attention Heatmap** visible  

Demo checklist: [`docs/demo_checklist.md`](docs/demo_checklist.md).

---

## Research limitations

- Trained on **HAM10000 only**; no guarantee on new devices, skin tones, or sites.
- **Single-fold** metrics; full CV and external validation are needed for serious benchmarking.
- Labels are a **research grouping**, not pathology ground truth.
- Grad-CAM shows **model sensitivity**, not causality or disease extent.

See [`docs/model_evaluation.md`](docs/model_evaluation.md) — *Model limitations*.

---

## Future roadmap

- Multi-fold evaluation and calibration analysis  
- Stronger clinical framing and external datasets  
- Optional LLM-generated lay explanations **from** model outputs only (never for diagnosis)

See [`docs/research_roadmap.md`](docs/research_roadmap.md).

---

## API snapshot (`POST /predict`)

Returns JSON including `prediction`, `risk_category`, `confidence`, `explanation`, `disclaimer`, and optionally Grad-CAM fields. See [`backend/README.md`](backend/README.md).

---

## License & citation

Use this repository in line with **HAM10000** and third-party licenses. Cite the dataset and this prototype appropriately in academic work.

---

## Repository contents note

- **Not included in git:** virtual environments, `node_modules`, local `archive/` images, `datasets/` caches, and `*.pt` checkpoints (see `models/checkpoints/README.md`).
- **Included:** source, docs, evaluation JSON and plots under `docs/assets/`, Grad-CAM code paths.
