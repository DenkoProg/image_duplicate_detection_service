from fastapi.testclient import TestClient
from app.main import app
from .test_helpers import generate_test_image

client = TestClient(app)


def test_add_images(client):
    image_data = generate_test_image()
    response = client.post(
        "/images",
        files={"files": ("test_image.jpg", image_data, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["added_count"] == 1


def test_add_images_no_input(client):
    response = client.post("/images")
    assert response.status_code == 400
    assert response.json()["detail"] == "No images provided"
