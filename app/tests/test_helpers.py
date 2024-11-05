from PIL import Image
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def generate_test_image(color="blue"):
    image = Image.new("RGB", (100, 100), color=color)
    byte_arr = io.BytesIO()
    image.save(byte_arr, format="JPEG")
    byte_arr.seek(0)
    return byte_arr


def upload_images_and_get_request_id(client, images):
    files = [("files", (f"test_image_{i}.jpg", img, "image/jpeg")) for i, img in enumerate(images)]
    response = client.post("/images", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    return data["request_id"]
