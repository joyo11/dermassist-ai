"""
Grad-CAM visualization for CNN explainability (research / education only).

Highlights regions of the input image that most influenced the score for the
chosen class. Not a clinical explanation of pathology.
"""

from __future__ import annotations

import base64
from io import BytesIO
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from app.models.model_loader import LoadedModel

_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)


def _target_layer(model: torch.nn.Module, model_name: str) -> torch.nn.Module:
    if model_name == "resnet50":
        return model.layer4[-1]
    if model_name == "efficientnet_b0":
        # Last MBConv block (spatial maps); torchvision's features[-1] is a 1×1 head conv.
        return model.features[-2]
    raise ValueError(f"Grad-CAM not configured for model_name={model_name}")


def _tensor_to_display_rgb(x01: np.ndarray) -> np.ndarray:
    """x01: H,W,3 in [0,1] float."""
    return (np.clip(x01, 0, 1) * 255).astype(np.uint8)


def generate_gradcam_png_base64(
    loaded: LoadedModel,
    input_tensor: torch.Tensor,
    *,
    target_class: Optional[int] = None,
) -> Optional[str]:
    """
    input_tensor: [1,3,224,224] normalized like training (requires_grad will be enabled here).

    Returns base64-encoded PNG (no data-URL prefix), or None on failure.
    """
    model_name = str(loaded.meta.get("model_name", ""))
    try:
        layer = _target_layer(loaded.model, model_name)
    except ValueError:
        return None

    model = loaded.model
    device = loaded.device
    model.eval()

    activations: list[torch.Tensor] = []
    gradients: list[torch.Tensor] = []

    def fwd_hook(_m, _inp, out):
        activations.append(out.detach())

    def full_backward_hook(_m, _gi, go):
        gradients.append(go[0].detach())

    h1 = layer.register_forward_hook(fwd_hook)
    h2 = layer.register_full_backward_hook(full_backward_hook)
    try:
        x = input_tensor.to(device).clone().detach().requires_grad_(True)
        logits = model(x)
        if target_class is None:
            target_class = int(torch.argmax(logits, dim=1).item())
        score = logits[0, target_class]
        model.zero_grad(set_to_none=True)
        score.backward()

        if not activations or not gradients:
            return None

        acts = activations[0]
        grads = gradients[0]
        if acts.dim() != 4 or grads.dim() != 4:
            return None

        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = (weights * acts).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam[0, 0].float().cpu().numpy()
        cam = cam - cam.min()
        denom = cam.max() + 1e-8
        cam = cam / denom

        # Map CAM to 224x224
        h, w = 224, 224
        cam_t = torch.from_numpy(cam).unsqueeze(0).unsqueeze(0)
        cam_up = F.interpolate(cam_t, size=(h, w), mode="bilinear", align_corners=False)
        cam_up = cam_up[0, 0].numpy()

        # Denormalize image for overlay
        img_np = x.detach().cpu().numpy()[0]
        img_np = img_np * _IMAGENET_STD[0] + _IMAGENET_MEAN[0]
        img_np = np.transpose(img_np, (1, 2, 0))
        img_np = np.clip(img_np, 0, 1)

        cmap = np.stack(
            [
                cam_up,
                np.zeros_like(cam_up),
                1.0 - cam_up,
            ],
            axis=-1,
        )
        overlay = 0.55 * img_np + 0.45 * cmap
        overlay_u8 = _tensor_to_display_rgb(overlay)

        buf = BytesIO()
        Image.fromarray(overlay_u8).save(buf, format="PNG")
        return base64.standard_b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return None
    finally:
        h1.remove()
        h2.remove()
        activations.clear()
        gradients.clear()
