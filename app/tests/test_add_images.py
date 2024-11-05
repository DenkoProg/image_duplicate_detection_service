from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from .test_helpers import generate_test_image

client = TestClient(app)


@patch("app.services.image_service.PineconeService.add_embeddings")
def test_add_images_with_mocked_pinecone(mock_add_embeddings, client):
    mock_add_embeddings.return_value = None

    image_data = generate_test_image()
    response = client.post(
        "/images",
        files={"files": ("test_image.jpg", image_data, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["added_count"] == 1
    mock_add_embeddings.assert_called_once()


def test_add_images_no_input(client):
    response = client.post("/images")
    assert response.status_code == 400
    assert response.json()["detail"] == "No images provided"
