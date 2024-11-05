import base64
from PIL import Image
import io


def decode_base64_image(b64_string: str) -> Image.Image:
    try:
        image_data = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        return image
    except Exception:
        raise ValueError("Invalid base64 image data")
