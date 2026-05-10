# DermAssist AI — Final Project Report

**Document type:** Technical summary for reviewers, recruiters, faculty, and AI researchers  
**Version:** Research prototype  
**Last updated:** May 2026  

---

## Abstract

DermAssist AI is a full-stack **research prototype** that demonstrates binary skin-lesion **risk screening** (research labels) on the public **HAM10000** dermoscopy dataset using deep convolutional networks—primarily **EfficientNet-B0** with ImageNet transfer learning—paired with optional **Grad-CAM** explainability and a **Next.js** / **FastAPI** demonstration stack. This report documents motivation, architecture, data protocol, training, quantitative evaluation on a held-out patient-aware split, explainability, deployment-oriented software design, ethics, limitations, and future work. **The system is not a medical device and not intended for clinical diagnosis.**

---

## 1. Introduction

### 1.1 Project overview

DermAssist AI combines:

- A **browser-based UI** for uploading dermoscopy-style images and viewing predictions with disclaimers.
- A **FastAPI** service that preprocesses images, runs PyTorch inference, and optionally returns Grad-CAM heatmaps as base64-encoded PNGs.
- **Training and evaluation scripts** (`models/train.py`, `models/evaluate.py`) for reproducible experiments on HAM10000 with stratified, **patient-aware** cross-validation.

The recommended serving checkpoint is **EfficientNet-B0** fine-tuned for the binary task (vs. a ResNet-50 baseline documented for comparison).

### 1.2 Why skin lesion screening matters

Melanoma and other skin cancers contribute substantially to morbidity and mortality. Early detection improves outcomes. At population scale, access to dermatology is uneven; tools that **assist triage or education** are widely discussed—provided they are validated, regulated where appropriate, and never substitute professional judgment.

### 1.3 Research motivation

This project explores whether **modern CNNs plus transparent visualization** can support **educational and workflow prototyping**: clear metrics on public data, explicit limitations, and UI patterns that reinforce “screening-style output only.” It is positioned as a **course-grade / portfolio-grade research artifact**, not a deployed clinical product.

---

## 2. Problem Statement

### 2.1 Challenges in early screening

Lesions vary in appearance; imaging quality and lighting differ; malignant cases may be rare relative to benign mimics. Reliable screening requires clinical correlation (history, full-body exam, dermoscopy expertise, biopsy when indicated).

### 2.2 Limitations of self-assessment

Patients may rely on apps or informal photos without standardized imaging or follow-up. Self-assessment **cannot** replace examination and diagnostic workup.

### 2.3 Why AI-assisted workflows are being explored

AI may help prioritize education, flag uncertain cases for review in controlled studies, or accelerate research datasets—but only with rigorous validation, fairness analysis, and governance. This prototype illustrates **technical plumbing and metrics**, not validated clinical utility.

---

## 3. System Architecture

End-to-end flow:

**Frontend (React / Next.js)** → **FastAPI backend** → **Preprocessing** → **EfficientNet-B0 (or ResNet-50)** → **Prediction + confidence** → **Grad-CAM (optional)** → **JSON response** → **UI rendering**

| Stage | Description |
|--------|-------------|
| **Frontend** | User uploads JPG/PNG; optional toggles (e.g., Grad-CAM); displays label band, confidence, disclaimers, and heatmap when returned. |
| **API** | `POST /predict` accepts `multipart/form-data` (`file`), optional `include_gradcam`. Returns structured JSON including prediction metadata and optional base64 heatmap. |
| **Preprocessing** | Resize to **224×224**, RGB, **ImageNet normalization**—aligned with training and Grad-CAM tensor paths. |
| **Model** | CNN loaded from `train.py` checkpoint (`DERMASSIST_CHECKPOINT`); binary logits → softmax → class and confidence. |
| **Grad-CAM** | Computes class-discriminative localization on the last convolutional stage appropriate to the architecture (e.g., EfficientNet MBConv block path used in code). |
| **UI** | Presents “model attention” language and disclaimers that the heatmap reflects **model internals**, not pathology. |

Further detail: [`system_architecture.md`](system_architecture.md).

---

## 4. Dataset — HAM10000

### 4.1 Scale and format

- **HAM10000** contains **10,015** labeled dermoscopic images (after standard filtering with valid paths in this project’s pipeline).
- Images span multiple diagnostic categories in the metadata (`dx`).

### 4.2 Diagnosis categories (multiclass origin)

HAM10000 uses seven coarse diagnostic codes (e.g., melanoma, basal cell carcinoma, benign nevus, etc.). Full multiclass training is optional in this codebase; the reported evaluation foregrounds the **binary mapping** below.

### 4.3 Binary label mapping (research design)

For the binary experiment:

| Binary label | Meaning (research) | Source diagnoses (`dx`) |
|--------------|-------------------|-------------------------|
| **0 — Benign** | Lower-risk group for screening-style experiments | `nv`, `bkl`, `df`, `vasc` |
| **1 — Potentially Malignant** | Higher-risk group for screening-style experiments | `mel`, `bcc`, `akiec` |

This aggregation is a **research convenience**, not a clinical definition of malignancy.

### 4.4 Train / validation split

Training uses **StratifiedGroupKFold** with **`n_splits = 5`**, **`shuffle = True`**, **`random_state = 42`**. Reported numbers use **fold 0**:

- **Training images (fold 0):** 8,012  
- **Validation images (fold 0):** 2,003  

Evaluation runs **only** on validation indices; training rows are excluded (`evaluate.py` asserts disjoint splits).

### 4.5 Patient-aware split

Splits group by **`lesion_id`** so that lesions from the **same patient** do not appear in both training and validation folds—reducing optimistic leakage that would inflate metrics.

---

## 5. Model Training

### 5.1 EfficientNet-B0

EfficientNet-B0 balances accuracy and efficiency via compound scaling; it serves as the **primary** architecture for deployment-oriented experiments in this repository.

### 5.2 Transfer learning

Weights are initialized from **torchvision ImageNet-pretrained** backbones, then fine-tuned end-to-end on HAM10000 binary labels.

### 5.3 Preprocessing pipeline

- Resize to **224×224**; training uses light augmentation suitable for dermoscopy (see `train.py`); validation uses deterministic eval transforms.

### 5.4 Hyperparameters (EfficientNet-B0, fold 0)

Representative values from saved training config:

| Setting | Value |
|---------|--------|
| Epochs | **10** |
| Batch size | **32** |
| Learning rate | **3e-4** |
| Optimizer | **AdamW** |
| Weight decay | **1e-4** |
| Loss | **CrossEntropyLoss** with **inverse-frequency class weights** from the training fold |
| Seed | **42** |

(ResNet-50 was trained under the same protocol for comparison.)

---

## 6. Model Evaluation

Unless noted, metrics below are for **EfficientNet-B0 on fold 0 validation only** (**N = 2,003** images). They are **research metrics on public data**, not clinical performance.

### 6.1 Primary metrics (EfficientNet-B0)

| Metric | Value | Plain English |
|--------|-------|----------------|
| **Accuracy** | **0.8782** (87.82%) | Fraction of validation images where the predicted class matches the research label. |
| **Precision (class 1)** | **0.6503** | Of all images predicted “Potentially Malignant,” about **65%** truly carried that label—many benigns predicted as malignant inflate false alarms. |
| **Recall (class 1)** | **0.8133** | Of all true “Potentially Malignant” images in this split, about **81%** were caught—some high-risk labels were missed (**false negatives**). |
| **F1 (class 1)** | **0.7227** | Harmonic balance of precision and recall for the positive class. |
| **ROC-AUC** | **0.9296** | Ability to rank malignant vs benign (threshold-independent discrimination). Higher is better; **not** a substitute for calibration or clinical validation. |

### 6.2 Confusion matrix (counts)

Rows = true label; columns = predicted label (**0 = Benign**, **1 = Potentially Malignant**):

|  | Predicted 0 | Predicted 1 |
|--|-------------|---------------|
| **True 0** | TN = **1441** | FP = **171** |
| **True 1** | FN = **73** | TP = **318** |

### 6.3 False positives and false negatives

- **False positives (171):** Benign-labeled images predicted as “Potentially Malignant” — unnecessary alarm / follow-up pressure in a hypothetical workflow.
- **False negatives (73):** “Potentially Malignant”–labeled images predicted benign — **dangerous if the tool were trusted as definitive**.

### 6.4 Comparison model (ResNet-50, same split)

ResNet-50 achieves slightly lower accuracy and ROC-AUC, **fewer false positives (87)** but **more false negatives (161)** on this fold. See [`model_evaluation.md`](model_evaluation.md) and JSON artifacts below.

### 6.5 Figures and machine-readable results

| Asset | Description |
|-------|-------------|
| [`assets/eval_efficientnet_b0_fold0.json`](assets/eval_efficientnet_b0_fold0.json) | Full EfficientNet-B0 metrics JSON |
| [`assets/eval_resnet50_fold0.json`](assets/eval_resnet50_fold0.json) | Full ResNet-50 metrics JSON |
| [`assets/confusion_matrix_efficientnet_b0_fold0.png`](assets/confusion_matrix_efficientnet_b0_fold0.png) | Confusion matrix plot |
| [`assets/roc_curve_efficientnet_b0_fold0.png`](assets/roc_curve_efficientnet_b0_fold0.png) | ROC curve |
| [`assets/pr_curve_efficientnet_b0_fold0.png`](assets/pr_curve_efficientnet_b0_fold0.png) | Precision–recall curve |

**Placeholder — screenshot:** *Insert UI screenshot of evaluation summary or dashboard here (`docs/screenshots/`).*  

---

## 7. Grad-CAM Explainability

### 7.1 What Grad-CAM is

**Gradient-weighted Class Activation Mapping (Grad-CAM)** visualizes which spatial regions of the input image most influenced the model’s score for a chosen class by combining feature-map activations with gradients of the class score.

### 7.2 Why explainability matters in healthcare AI

Stakeholders expect transparency: **what drove the score?** Explainability supports debugging and communication—but must not be mistaken for causal medical reasoning.

### 7.3 What the heatmap means here

The overlay highlights regions that **increased the model’s activation path** toward the predicted class under this architecture and preprocessing. It is **not** a biomarker map or histopathology explanation.

### 7.4 Limitations of heatmaps

Heatmaps can be **unstable**, sensitive to preprocessing, **not faithful** to pixel-level causality, and **misleading** if shown without disclaimers. They must not replace clinician judgment.

**Placeholder — Grad-CAM figure:** *Insert example heatmap pair (input + overlay) for EfficientNet-B0 here.*

---

## 8. Frontend and Backend

### 8.1 Frontend

- **Framework:** Next.js (React).
- **Role:** Image upload, API calls, results presentation, disclaimer banners, optional heatmap display.

### 8.2 Backend

- **Framework:** FastAPI.
- **Inference:** Loads checkpoint from `DERMASSIST_CHECKPOINT` when valid; otherwise falls back to placeholder inference for UI wiring (documented in `backend/README.md`).

### 8.3 Image upload flow

User selects file → frontend posts to `/predict` → backend preprocesses → model forward pass → JSON returned → UI renders prediction and optional Grad-CAM image.

### 8.4 API and inference pipeline

- **Endpoint:** `POST /predict` (`multipart/form-data`, field `file`; optional `include_gradcam`).
- **Pipeline:** decode bytes → preprocess tensor → forward → softmax → optional Grad-CAM → JSON schema documented in backend README.

**Placeholder — screenshot:** *Insert sequence diagram or API screenshot (`docs/screenshots/`).*  

---

## 9. Ethical Considerations

| Topic | Position |
|-------|----------|
| **Not a diagnosis tool** | Outputs are educational / research screening-style only. |
| **False-negative risk** | Any negative or low-risk presentation **does not** exclude malignancy. |
| **Dataset bias** | HAM10000 may under-represent demographics, devices, and lesion distributions vs. real clinics. |
| **Public dataset limits** | Single-source training cannot establish generalization or fairness. |
| **Research-only** | No regulatory clearance; no deployment claim. |

---

## 10. Limitations

1. **No prospective clinical validation** — Metrics are retrospective on public data.
2. **Single-dataset training** — Limited external validity.
3. **Single-fold spotlight** — Best practice would report **full cross-validation** and uncertainty across folds.
4. **No deployment approval** — Not FDA-cleared / CE-marked; not intended for patient-facing diagnosis.

---

## 11. Future Work

- Additional **datasets** and **external validation** cohorts.
- **Full k-fold reporting**, calibration (temperature scaling / Platt), and threshold optimization with explicit cost matrices.
- **Clinician-in-the-loop** studies for usability and safety.
- **Prospective** acquisition protocols.
- **Mobile** optimization and latency-aware deployment research.
- Stronger **explainability** (uncertainty quantification, ensemble disagreement, sanity checks).

---

## 12. Conclusion

DermAssist AI demonstrates an **end-to-end research stack**—HAM10000 binary screening experiments with EfficientNet-B0, quantitative evaluation on a patient-aware split, Grad-CAM overlays, and a modern web demo—with **explicit ethical framing**. The contribution is **engineering and reporting transparency** for education and discussion, not clinical efficacy. Responsible next steps are external validation, broader fairness analysis, and regulated pathways only where legally required.

---

## References and artifacts

- Tschandl, P., Rosendahl, C., Kittler, H. HAM10000 dataset (see dataset license and citation requirements when publishing).
- Internal: [`model_evaluation.md`](model_evaluation.md), [`system_architecture.md`](system_architecture.md), [`disclaimer.md`](disclaimer.md).

---

## Appendix — Metric glossary (simple English)

| Term | Meaning |
|------|---------|
| **Accuracy** | Overall fraction correct—can hide imbalance. |
| **Precision** | When the model says “malignant,” how often it is right (for that label definition). |
| **Recall** | Of all true malignants (under the label mapping), how many the model finds. |
| **F1** | Balance of precision and recall for a class. |
| **ROC-AUC** | Rank quality across thresholds when separating the two classes. |

---

*This document is part of the DermAssist AI research prototype repository and does not constitute medical or regulatory advice.*
