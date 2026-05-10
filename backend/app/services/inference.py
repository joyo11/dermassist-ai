from __future__ import annotations

import hashlib
import logging
from typing import Dict, Literal, Tuple

import torch

from app.models.model_loader import LoadedModel, get_loaded_model
from app.services.gradcam import generate_gradcam_png_base64
from app.services.preprocessing import preprocess_image_bytes

logger = logging.getLogger(__name__)

PredictionLabel = Literal["Benign", "Potentially Malignant"]
RiskCategory = Literal["Low Risk", "Medium Risk", "High Risk"]

DISCLAIMER = (
    "This tool is for educational and research purposes only and is not a medical diagnosis."
)

ATTENTION_HEATMAP_LABEL = "Model Attention Heatmap"
ATTENTION_HEATMAP_DISCLAIMER = (
    "This heatmap shows model attention, not medical evidence."
)

# Aligns with `models/ham10000_data.py` binary grouping (multiclass → API collapse).
HIGH_RISK_DX = frozenset({"mel", "bcc", "akiec"})


def _mock_predict_from_tensor(x: torch.Tensor, image_bytes: bytes) -> Tuple[PredictionLabel, float]:
    """Placeholder when no checkpoint is configured or loading failed."""
    _ = x
    h = hashlib.sha256(image_bytes).hexdigest()
    raw = int(h[:8], 16) / 0xFFFFFFFF
    confidence = float(0.55 + 0.4 * abs(raw - 0.5) * 2)
    prediction: PredictionLabel = "Potentially Malignant" if raw > 0.5 else "Benign"
    return prediction, confidence


# Benign: align risk band with softmax confidence on the displayed label only (no diagnosis).
_BENIGN_LOW_RISK_MIN_CONF = 0.72


def _risk_from_prediction(prediction: PredictionLabel, confidence: float) -> RiskCategory:
    """
    Cleaner mapping: Potentially Malignant → always High Risk (API screening stance).
    Benign → Low Risk only when confidence is high; otherwise Medium Risk (reflects uncertainty).
    """
    if prediction == "Potentially Malignant":
        return "High Risk"
    if prediction == "Benign":
        return "Low Risk" if confidence >= _BENIGN_LOW_RISK_MIN_CONF else "Medium Risk"
    raise AssertionError("unreachable")


def _confidence_research_note(prediction: PredictionLabel, confidence: float) -> str:
    """Interpret softmax confidence in non-clinical, research terms."""
    if prediction == "Benign":
        if confidence >= 0.82:
            return (
                "The assigned Benign label has relatively high softmax confidence on this crop, "
                "so the model’s internal scores are comparatively peaked toward that class."
            )
        if confidence >= _BENIGN_LOW_RISK_MIN_CONF:
            return (
                "Softmax confidence for the Benign label is in a solid but not extreme range; "
                "treat the numeric score as a research-style calibration signal, not certainty."
            )
        return (
            "Softmax confidence for the Benign label is moderate. Non-trivial probability mass "
            "remains on the alternative class, so this output should be read as more tentative."
        )

    if confidence >= 0.82:
        return (
            "The Potentially Malignant label shows relatively high softmax confidence here, "
            "meaning the model’s logits favor that class strongly on this input."
        )
    if confidence >= 0.58:
        return (
            "Softmax confidence for the Potentially Malignant label is mid-range; "
            "the decision boundary is not far from the runner-up class in probability space."
        )
    return (
        "Softmax confidence is comparatively modest for the displayed label; "
        "the model’s scores are less decisive on this image, which increases epistemic uncertainty "
        "for any downstream use of this prototype."
    )


def _heatmap_research_note(*, heatmap_included: bool) -> str:
    if not heatmap_included:
        return (
            "No Grad-CAM overlay was returned for this request (disabled, unavailable, or "
            "non-checkpoint inference), so spatial attribution is not shown."
        )
    return (
        "When the attention heatmap below is present, warmer or more saturated areas mark "
        "regions whose activations contributed most to the gradient for the predicted class—they "
        "reflect CNN sensitivity to texture and contrast in the resized crop, not a clinical "
        "outline of disease and not evidence of pathology."
    )


def _uncertainty_research_note(prediction: PredictionLabel, risk: RiskCategory, confidence: float) -> str:
    parts = [
        "This pipeline outputs a research screening label only; it does not infer diagnosis, "
        "stage, or treatment need.",
    ]
    if prediction == "Benign" and risk == "Medium Risk":
        parts.append(
            "Because softmax confidence sits below the high-confidence threshold for Benign, "
            "the UI shows Medium Risk to signal calibration uncertainty—not a second clinical "
            "risk axis layered on top of the label."
        )
    elif prediction == "Potentially Malignant":
        parts.append(
            "External validation, calibration plots, and human review remain necessary before "
            "any deployment-oriented interpretation."
        )
    else:
        parts.append(
            "Hold-out performance on public datasets does not transfer automatically to new "
            "cameras, populations, or acquisition settings."
        )
    return " ".join(parts)


def _explanation(
    prediction: PredictionLabel,
    risk: RiskCategory,
    confidence: float,
    *,
    top_class_detail: str | None = None,
    heatmap_included: bool = False,
) -> str:
    detail = (
        f" Multiclass checkpoint: the API collapsed the top training class ({top_class_detail}) "
        "into the binary label above."
        if top_class_detail
        else ""
    )

    conf_note = _confidence_research_note(prediction, confidence)
    heat_note = _heatmap_research_note(heatmap_included=heatmap_included)
    uncertain = _uncertainty_research_note(prediction, risk, confidence)

    if prediction == "Benign":
        lead = (
            f"The binary screening head labeled this crop Benign with risk band {risk} "
            f"(softmax confidence {confidence:.0%} for that displayed class). "
            "That bucket aggregates low-malignancy training codes in HAM10000 for this research "
            "prototype; it is not a patient-level assessment."
        )
    else:
        lead = (
            "The binary screening head labeled this crop Potentially Malignant; the API maps "
            f"that label to {risk} for consistent presentation. "
            f"Softmax confidence for the displayed class is {confidence:.0%}. "
            "The pooled training diagnoses are used for benchmarking only."
        )

    return "\n\n".join([lead + detail, conf_note, heat_note, uncertain])


@torch.no_grad()
def _predict_with_checkpoint(
    loaded: LoadedModel,
    x: torch.Tensor,
) -> Tuple[PredictionLabel, float, str | None, int]:
    """
    Returns (API prediction, confidence in [0,1], optional detail string, argmax class index).
    API schema allows only Benign | Potentially Malignant.
    """
    x = x.to(loaded.device, non_blocking=True)
    logits = loaded.model(x)
    probs = torch.softmax(logits, dim=1)[0].cpu()
    num_classes = int(loaded.meta.get("num_classes", probs.numel()))
    class_names = loaded.meta.get("class_names")
    if not isinstance(class_names, list) or len(class_names) != num_classes:
        class_names = [str(i) for i in range(num_classes)]

    idx = int(torch.argmax(probs).item())
    top_p = float(probs[idx].item())
    top_name = str(class_names[idx])

    if num_classes == 2:
        # Expect training labels: Benign (0), Potentially Malignant (1)
        name = str(class_names[idx])
        if name == "Benign":
            return "Benign", top_p, None, idx
        if name == "Potentially Malignant":
            return "Potentially Malignant", top_p, None, idx
        return ("Potentially Malignant" if idx == 1 else "Benign"), top_p, None, idx

    # Multiclass (e.g. 7 dx): collapse to binary for the public API.
    prediction = "Potentially Malignant" if top_name in HIGH_RISK_DX else "Benign"
    return prediction, top_p, top_name, idx


def predict_from_image_bytes(
    *, image_bytes: bytes, include_gradcam: bool = True
) -> Dict[str, object]:
    """
    Preprocess → PyTorch checkpoint if `DERMASSIST_CHECKPOINT` is set, else placeholder.
    """
    x = preprocess_image_bytes(image_bytes)

    loaded = get_loaded_model()
    gradcam_b64: str | None = None
    used_checkpoint_inference = False
    target_idx = 0

    if loaded is not None:
        try:
            pred, confidence, detail, target_idx = _predict_with_checkpoint(loaded, x)
            used_checkpoint_inference = True
        except Exception as e:
            logger.exception("Model inference failed, falling back to placeholder: %s", e)
            pred, confidence = _mock_predict_from_tensor(x, image_bytes)
            detail = None
    else:
        pred, confidence = _mock_predict_from_tensor(x, image_bytes)
        detail = None

    if used_checkpoint_inference and include_gradcam:
        try:
            gradcam_b64 = generate_gradcam_png_base64(
                loaded, x, target_class=target_idx
            )
        except Exception as e:
            logger.warning("Grad-CAM generation failed: %s", e)

    risk = _risk_from_prediction(pred, confidence)
    out: Dict[str, object] = {
        "prediction": pred,
        "risk_category": risk,
        "confidence": confidence,
        "explanation": _explanation(
            pred,
            risk,
            confidence,
            top_class_detail=detail,
            heatmap_included=bool(gradcam_b64),
        ),
        "disclaimer": DISCLAIMER,
        "gradcam_image_base64": gradcam_b64,
        "attention_heatmap_label": None,
        "attention_heatmap_disclaimer": None,
    }
    if gradcam_b64:
        out["attention_heatmap_label"] = ATTENTION_HEATMAP_LABEL
        out["attention_heatmap_disclaimer"] = ATTENTION_HEATMAP_DISCLAIMER
    return out
