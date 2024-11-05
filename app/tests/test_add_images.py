from fastapi.testclient import TestClient
from app.main import app
from PIL import Image
import io

client = TestClient(app)


def generate_test_image():
    image = Image.new('RGB', (100, 100), color='blue')
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return byte_arr


def test_add_images_no_input():
    response = client.post("/images")
    assert response.status_code == 400
    assert response.json()["detail"] == "No images provided"


def test_add_images_multipart():
    image_data = generate_test_image()
    response = client.post(
        "/images",
        files={"files": ("test_image.jpg", image_data, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["added_count"] == 1
