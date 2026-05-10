from typing import Literal

from pydantic import BaseModel, Field


RiskCategory = Literal["Low Risk", "Medium Risk", "High Risk"]
PredictionLabel = Literal["Benign", "Potentially Malignant"]


class PredictionResponse(BaseModel):
    prediction: PredictionLabel
    risk_category: RiskCategory
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    disclaimer: str
    # Base64-encoded PNG (no data-URL prefix); omitted when unavailable (e.g. placeholder model).
    gradcam_image_base64: str | None = None
    # Set when Grad-CAM PNG is returned (research / education only).
    attention_heatmap_label: str | None = None
    attention_heatmap_disclaimer: str | None = None

