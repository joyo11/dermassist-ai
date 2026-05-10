# DermAssist AI — Clinical Feedback Packet

**Audience:** Doctors, dermatologists, clinics, hospitals (non-technical overview)  
**Purpose:** Explain what this research prototype is, what it does **not** do, and how we are seeking **professional perspective**—not patient care decisions based on this tool.  

**Important:** DermAssist AI is **not** a diagnostic device. It has **not** been reviewed by FDA or similar regulators for medical use. It is **not** approved for clinical deployment.

---

## What is DermAssist AI?

DermAssist AI is a **research demonstration** that combines:

- A simple web upload screen.
- A computer model (**EfficientNet-B0**) trained on the **public HAM10000** skin lesion image collection.

The system produces a **research-style screening label** (“Benign” vs “Potentially Malignant”) and may show a **colored heatmap** indicating where the model focused visually. It is meant for **discussion, education, and workflow feedback**—**not** for diagnosing patients.

---

## What does the model actually do?

The model looks at **patterns in the image pixels**—texture, color, and structure—that it learned from thousands of **labeled research images**. It compares a new image to patterns seen during training and outputs:

- A **category** (research grouping described below).
- A **confidence score** that reflects how strongly the model’s math favors one category over the other—not clinical certainty.

This is **pattern recognition on photographs**, not an examination, not a biopsy, and not a substitute for clinical judgment.

---

## What “Benign” vs “Potentially Malignant” means here

These labels come from a **research grouping** of public dataset categories—not from a pathologist’s diagnosis of your patient.

- **“Benign” (research label)** corresponds to a lower-risk group of diagnoses used in our training setup.
- **“Potentially Malignant” (research label)** corresponds to a higher-risk group used for screening-style experiments.

**These names do not mean the lesion is truly benign or malignant in real life.** They only describe how we grouped labels for research.

---

## What the Grad-CAM heatmap shows

When a heatmap is displayed, it highlights areas of the image that **most influenced the model’s score** for its prediction. Think of it as “where the computer looked hardest”—**not** “where the cancer is,” and **not** proof that an area is abnormal.

Heatmaps can be influenced by lighting, blur, hair, rulers, or background skin. They should **never** replace dermoscopy skill or biopsy decisions.

---

## What the confidence score means

The confidence score is a **technical measure** from the model’s output. A higher score means the model is **more decisive** between its labels—not that the finding is medically more certain or “more dangerous.” Low confidence does **not** guarantee safety, and high confidence does **not** prove disease.

---

## What we need you to understand about mistakes

- The system **can be wrong**.
- **False negatives are possible:** the tool may suggest “Benign” when, in reality, a concerning lesion would warrant evaluation.
- **False positives are possible:** the tool may raise concern when clinical judgment would not.

**Clinicians should not rely on this system for patient care.** It does not replace history, full skin exam, dermoscopy training, or indicated biopsy and pathology.

---

## How this relates to public datasets

The model was trained on **HAM10000**, a **public** set of dermoscopy images from past research. Real clinics see different cameras, skin tones, lesion types, and workflows. Performance on public data **does not** predict performance in your practice.

---

## 1. Why we built this

We built DermAssist AI to:

- Show how modern AI **pipelines** can be connected to transparent explanations (heatmaps) and clear disclaimers.
- Invite **honest clinical feedback** on whether such tools could ever be useful in **controlled research**—and where they fail or cause harm if misunderstood.

We are **not** claiming this tool is ready for patients.

---

## 2. Current capabilities

- Upload an image and receive a **research screening-style** label and confidence.
- Optionally view a **heatmap** of model attention.
- Read built-in reminders that output is **not** diagnostic.

---

## 3. Current limitations

- **No clinical validation** in real practices or prospective trials.
- **Single public dataset** training—limited diversity and realism.
- **No external validation** on independent hospital data in this prototype’s reporting.
- **No regulatory approval** for medical use.
- Heatmaps show **model behavior**, not confirmed pathology.

---

## 4. What feedback we are requesting

We welcome professional input on:

- Whether the **language and disclaimers** are clear enough to reduce misunderstanding.
- Whether the **heatmap presentation** risks being interpreted as diagnostic “localization.”
- What **evidence** would be needed before **any** future study involving clinicians or patients.
- Practical barriers (workflow, liability, imaging quality) even if the technology improved.

---

## 5. What we are NOT requesting

- We are **not** asking you to use this tool to diagnose or treat patients.
- We are **not** asking you to endorse safety or efficacy for clinical use.
- We are **not** implying regulatory clearance or hospital readiness.

---

## 6. Privacy statement

This research prototype is intended for **local or controlled demos**. If images are sent to a server, they should be handled under policies appropriate to your institution. **Do not upload real patient images** unless you have proper authorization, consent, and compliance review. For demonstrations, use **de-identified** or **public** example images only.

When in doubt, **do not** upload clinical data to external systems.

---

## 7. Future research direction

Possible next steps—subject to ethics approval and regulation—include:

- Studies with **more diverse datasets** and **independent validation**.
- **Prospective** workflows with supervised use only.
- Collaboration with dermatologists on **safe presentation** of AI outputs.
- Clear separation between **research demos** and any future regulated product development.

---

## Summary

DermAssist AI analyzes **visual patterns** learned from a **public** skin lesion dataset and produces **research screening-style** outputs and optional attention maps only. It is **not** a diagnosis, **not** FDA-approved, and **must not** guide patient care. We seek **professional critique** to keep expectations realistic and safety central.

---

**Placeholder — product screenshot:** *[Insert neutral demo screenshot here — no patient identifiable information.]*  

**Placeholder — example heatmap:** *[Insert example heatmap with caption: “Model attention only—not pathology.”]*  

---

*For technical detail, see `docs/final_project_report.md` and `docs/model_evaluation.md`. For full disclaimer text, see `docs/disclaimer.md`.*
