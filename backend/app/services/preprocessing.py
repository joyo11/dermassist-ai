from io import BytesIO

from PIL import Image
import torch
from torchvision import transforms


_IMAGENET_MEAN = (0.485, 0.456, 0.406)
_IMAGENET_STD = (0.229, 0.224, 0.225)


_preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=_IMAGENET_MEAN, std=_IMAGENET_STD),
    ]
)


def preprocess_image_bytes(image_bytes: bytes) -> torch.Tensor:
    """
    Preprocessing pipeline for a typical ImageNet-pretrained CNN:
    - open image with PIL
    - convert to RGB
    - resize to 224x224
    - normalize using ImageNet mean/std
    - convert to tensor (returned as a batched tensor: [1, 3, 224, 224])
    """
    try:
        img = Image.open(BytesIO(image_bytes))
    except Exception as e:
        raise ValueError("Unable to read image. Please upload a valid JPG/PNG.") from e

    img = img.convert("RGB")
    tensor = _preprocess(img).unsqueeze(0)
    return tensor

