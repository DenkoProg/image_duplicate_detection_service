from fastapi.testclient import TestClient
from app.main import app
from .test_helpers import generate_test_image, upload_images_and_get_request_id

client = TestClient(app)


def test_search_duplicates(client):
    image = generate_test_image(color="red")
    request_id = upload_images_and_get_request_id(client, [image])

    response = client.get(f"/duplicates/{request_id}")

    assert response.status_code == 200
    data = response.json()
    assert "duplicates" in data
    assert len(data["duplicates"]) > 0
    assert data["duplicates"][0]["image_id"] == "mocked_id_1"
    assert data["duplicates"][0]["score"] == 0.9
    assert "metadata" in data["duplicates"][0]


def test_search_duplicates_invalid_request_id(client):
    response = client.get("/duplicates/invalid-id")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No duplicates found."


def test_search_duplicates_no_duplicates(client):
    image = generate_test_image(color="green")
    request_id = upload_images_and_get_request_id(client, [image])

    response = client.get(f"/duplicates/{request_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No duplicates found."
