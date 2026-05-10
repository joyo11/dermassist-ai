# Clinical feedback proposal — DermAssist AI (research)

## Disclaimer

**DermAssist AI is not a medical device, not FDA-cleared or CE-marked, and not intended for diagnosis or treatment.** This document describes a **research and education** prototype and a request for **non-clinical workflow feedback** only.

---

## 1. Project overview

DermAssist AI is a **research prototype** that combines:

- A **web interface** for uploading a skin lesion image (JPG/PNG).
- A **Python API** that runs a convolutional neural network trained on the public **HAM10000** dataset.
- Outputs framed as **risk screening-style** labels (e.g. benign vs potentially malignant) with confidence, disclaimers, and optional **Grad-CAM** attention maps for model interpretability research.

The goal is to explore how such tools might **support education and future research**, not to replace clinical examination.

---

## 2. Problem statement

Access to dermatology can be limited; there is research interest in **decision support** and **triage education**. Any serious prototype must:

- Avoid **diagnostic claims**.
- Communicate **uncertainty** and **error modes** (false positives / false negatives).
- Be evaluated with **clinician input** before further technical investment.

We seek structured feedback from dermatologists and clinic staff on **messaging, workflow fit, and research direction** — not validation on patients in this phase.

---

## 3. Current system (technical summary)

- **Frontend:** Next.js web app — image upload, results, disclaimers.
- **Backend:** FastAPI — `POST /predict` (multipart image), optional Grad-CAM overlay in the JSON response.
- **Model:** Binary classifiers (ResNet-50 and/or EfficientNet-B0) trained on HAM10000 with a defined mapping from pathology codes to **research** “benign” vs “potentially malignant” groups.
- **Evaluation:** Documented in `docs/model_evaluation.md` (single fold metrics, confusion matrices, ROC/PR plots).

---

## 4. Current model results (summary)

On **fold 0** validation (patient-aware split), **EfficientNet-B0** achieved higher accuracy and ROC-AUC than **ResNet-50** in our last run; both models show **substantial false positive rates** and **non-zero false negatives**. Full tables, FP/FN counts, and plots are in **`docs/model_evaluation.md`**.

These numbers are **not** generalizable clinical performance; they are **internal research metrics** on public data.

---

## 5. What we are asking from dermatologists / clinics

We invite **voluntary, unpaid research feedback** on topics such as:

- Whether the **disclaimers and risk wording** are appropriate and clear.
- Whether the **output format** (label, confidence, explanation, heatmap) is useful for **teaching** or misleading if misread.
- **Workflow considerations:** how a research demo should be presented (e.g. only in academic settings, with facilitator present).
- Suggestions for **future study design** (e.g. external datasets, reader studies — without committing to them now).

We are **not** asking reviewers to rely on the tool for care decisions.

---

## 6. Data and privacy — initial phase

- **No patient data is requested** for this feedback round.
- Reviewers may use **public example images** or their own **non-patient** teaching images if they choose.
- We are **not** asking clinics to export EMR data or identifiable patient images.

---

## 7. Deployment

- **No clinical deployment is requested** as part of this proposal.
- The software is intended for **local or controlled research demos**, not integration into EHR or billing workflows.

---

## 8. Scope of feedback

We seek **research feedback and workflow review** only, for example:

- UX and safety messaging.
- Suitability for **education** vs **clinical-like** framing.
- Gaps that would need to be addressed before any **future** formal study (e.g. IRB-approved reader study).

---

## 9. Regulatory / product status

**This is not a medical device.** It has not undergone regulatory review. It must not be marketed for diagnosis or treatment. Any future path toward clinical research would require separate legal, ethical, and regulatory planning.

---

## 10. Contact and materials

- Technical evaluation: `docs/model_evaluation.md`
- One-page overview for busy clinicians: `docs/one_page_clinical_summary.md`
- Demo steps: `docs/demo_checklist.md`

Thank you for considering participation in this **research-oriented** review.
