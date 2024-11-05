from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.vector_storage_service import PineconeService
import pytest
import pinecone
from app.config import settings
from pinecone import ServerlessSpec

TEST_INDEX_NAME = f"{settings.pinecone_index_name}-test"


@pytest.fixture(scope="module", autouse=True)
def setup_pinecone_test_index():
    pc = pinecone.Pinecone(api_key=settings.pinecone_api_key)

    if TEST_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=TEST_INDEX_NAME,
            dimension=2048,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1',
            )
        )

    original_index_name = settings.pinecone_index_name
    settings.pinecone_index_name = TEST_INDEX_NAME

    yield

    pc.delete_index(TEST_INDEX_NAME)

    settings.pinecone_index_name = original_index_name


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def mock_pinecone_service():
    with pytest.MonkeyPatch.context() as m:
        mock_service = MagicMock(spec=PineconeService)
        m.setattr("app.services.image_service.PineconeService", mock_service)
        yield mock_service
