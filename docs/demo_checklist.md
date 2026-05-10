# Demo checklist — DermAssist AI (research)

Use this list when showing the prototype to colleagues or clinical reviewers. **Do not present the tool as diagnostic.**

---

## Before the demo

- [ ] Read **`docs/model_evaluation.md`** — know FP/FN rates and limitations.
- [ ] Read **`docs/one_page_clinical_summary.md`** or **`docs/clinical_feedback_proposal.md`** for framing.
- [ ] Set **`DERMASSIST_CHECKPOINT`** to a trained `.pt` file if you want **real** model output and **Grad-CAM** (not placeholder).
  - Example:  
    `export DERMASSIST_CHECKPOINT="$PWD/models/checkpoints/best_binary_efficientnet_b0_fold0.pt"`

---

## Run backend

- [ ] `cd dermassist-ai/backend`
- [ ] `source venv/bin/activate` (or use your Python env with dependencies installed)
- [ ] `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- [ ] Check `http://127.0.0.1:8000/health` → `{"status":"ok"}`

---

## Run frontend

- [ ] `cd dermassist-ai/frontend`
- [ ] `npm run dev`
- [ ] Open the URL shown (e.g. `http://localhost:3000`)

---

## During the demo

- [ ] **Upload a test image** (JPG/PNG) — public dermoscopy example or non-patient teaching image only.
- [ ] **Show the result** — label, confidence, explanation.
- [ ] **Show the disclaimer** in the UI (banner + results notice).
- [ ] **Show limitations** — public dataset only, not clinically validated, FP/FN risk, not a diagnosis (`docs/model_evaluation.md`).
- [ ] **Show Grad-CAM** (if checkpoint loaded) — explain it shows **model attention**, not histology or certainty.
- [ ] **Explain future work** — more training, cross-validation, external data, formal clinician studies, regulatory path *if ever* considered.

---

## After the demo

- [ ] Collect **research feedback** (messaging, safety, education value) — not patient outcomes.
- [ ] **No patient data** should be collected for this informal review unless a separate approved study is in place.

---

## If something fails

- **“Failed to fetch”** — backend not running or wrong port; check `NEXT_PUBLIC_API_URL` / `VITE_API_URL` in `frontend/.env.local`.
- **No heatmap** — placeholder mode, Grad-CAM error, or `include_gradcam=false` in the API request.
