from fastapi.testclient import TestClient
from app.main import app
from PIL import Image
import io

client = TestClient(app)


def generate_test_image(color='blue'):
    image = Image.new('RGB', (100, 100), color=color)
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return byte_arr


def upload_images_and_get_request_id(images):
    files = [("files", (f"test_image_{i}.jpg", img, "image/jpeg")) for i, img in enumerate(images)]
    response = client.post("/images", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    return data["request_id"]


def test_search_duplicates_invalid_request_id():
    response = client.get("/duplicates/invalid-id")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No duplicates found or invalid request_id."


def test_search_duplicates_no_duplicates():
    image = generate_test_image(color='green')
    request_id = upload_images_and_get_request_id([image])

    response = client.get(f"/duplicates/{request_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No duplicates found." or data["message"] == "No duplicates found or invalid request_id."


def test_search_duplicates_with_duplicates():
    image1 = generate_test_image(color='red')
    image2 = generate_test_image(color='red')
    request_id = upload_images_and_get_request_id([image1, image2])

    response = client.get(f"/duplicates/{request_id}")
    assert response.status_code == 200
    data = response.json()
    assert "duplicates" in data
    assert len(data["duplicates"]) > 0

    for duplicate in data["duplicates"]:
        assert "image_id" in duplicate
        assert "score" in duplicate
        assert duplicate["score"] > 0
        assert "metadata" in duplicate


