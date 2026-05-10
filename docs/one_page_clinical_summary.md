# DermAssist AI — one-page summary for clinicians

## What this is

**DermAssist AI** is a **research and teaching demo**, not a medical product. It is **not** a diagnosis and **not** cleared as a medical device. It runs a computer model on a **single skin photo** and shows a **screening-style** result plus an optional **heatmap** of where the model focused.

---

## Why we built it

We are exploring how **transparent, disclaimer-heavy AI demos** might support **education and future research** on skin lesions — and where they could mislead if used like a diagnostic test.

---

## What the model does

- Trained only on the public **HAM10000** dataset (dermoscopy images).
- Outputs a **binary research label**: “benign” vs “potentially malignant” based on a **defined mapping** of dataset labels — **not** a pathologic diagnosis.
- **Makes mistakes:** it can flag benign lesions as high concern (**false alarms**) and can **miss** some higher-risk cases (**false negatives**). Your own judgment always comes first.

---

## What we want from you

Short **feedback** (email or call) on:

- Is the **wording** honest and safe for learners?
- Is the **heatmap** helpful for teaching, or confusing?
- What would you **never** want a tool like this to claim without strong evidence?

We are **not** asking you to use this on patients or to send us patient data.

---

## What we are *not* doing now

- **No** clinical rollout or EHR integration.  
- **No** request for identifiable patient images.  
- **No** claim that the model is accurate enough for real-world screening.

---

## If you agree to look at the demo

You’ll need a laptop running the app locally (or a shared screen in a research meeting). See **`docs/demo_checklist.md`** for steps.

---

## Bottom line

**This is a research prototype to discuss safety, limits, and education — not a tool for patient care.**

For numbers and limitations, see **`docs/model_evaluation.md`**.
