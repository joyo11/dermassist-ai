from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.inference import predict_from_image_bytes
from app.utils.schemas import PredictionResponse

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    include_gradcam: bool = Form(default=True),
) -> PredictionResponse:
    """
    Accepts an uploaded JPG/PNG image, runs preprocessing + inference, and returns
    an AI-assisted *risk screening* result for research/education.

    Optional Grad-CAM: when `include_gradcam` is true (default) and a checkpoint is loaded,
    the response may include `gradcam_image_base64` plus `attention_heatmap_label` and
    `attention_heatmap_disclaimer`.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    content_type = (file.content_type or "").lower()
    allowed = {"image/jpeg", "image/png"}
    if content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPG or PNG image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = predict_from_image_bytes(
            image_bytes=image_bytes, include_gradcam=include_gradcam
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # Avoid leaking internal errors; keep message user-friendly.
        raise HTTPException(
            status_code=500, detail="Failed to analyze image. Please try again."
        ) from e

    return PredictionResponse(**result)

