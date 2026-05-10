# DermAssist AI — Project Proposal (Research Prototype)

## Problem statement

Skin cancer and other serious dermatologic conditions can benefit from **early clinician evaluation**. However, many people face barriers to timely access, and non-expert self-assessment can be unreliable. There is research interest in **AI-assisted risk screening** as a supportive tool to help prioritize clinical review and expand access to educational resources.

## Why early screening matters

Early clinician assessment can improve outcomes for some conditions and reduce delays in care. A safe research prototype must avoid overclaiming and must be designed to **encourage clinical follow-up**, not replace it.

## Proposed AI solution

DermAssist AI is a **computer-vision-based** research prototype:

- Users upload a JPG/PNG image of a skin lesion.
- A PyTorch vision model generates a **risk screening output** (educational/research).
- The UI displays prediction label, risk category, confidence, explanation, and a prominent disclaimer.

The product will **never claim diagnosis**. It will describe outputs as screening/risk signals for research and education only.

## Research phases

### 1) Public dataset testing phase

- Train and validate on public datasets (HAM10000 / ISIC).
- Establish reproducible preprocessing and evaluation.
- Document label mapping decisions and limitations.

### 2) Model comparison phase

- Compare architectures (ResNet50, EfficientNet variants).
- Study robustness to lighting, camera quality, and cropping.
- Evaluate calibration and uncertainty estimation (optional).
- Add explainability experiments (Grad-CAM) for research interpretability.

### 3) Clinical/research collaboration phase (only with oversight)

- Engage clinicians and researchers.
- Seek appropriate approvals (e.g., IRB where applicable).
- Validate on external data and/or prospective studies when feasible.
- Ensure clinician-in-the-loop review and safe UX messaging.

## Limitations

- Public datasets may not represent real-world diversity (skin tone, lesion types, imaging conditions).
- Models may produce false positives/false negatives.
- Model confidence is **not** clinical certainty.
- This prototype is not intended for clinical decision-making.

## Ethical considerations

- Bias and fairness across skin tones and demographics
- Safety messaging to discourage self-diagnosis
- Privacy considerations for medical images
- Transparency about model limitations and validation

## Required disclaimer

DermAssist AI is an **educational and research** prototype and is **not** a medical diagnosis tool. Users should consult a licensed clinician for medical concerns.

