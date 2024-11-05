import uuid
from typing import List
from fastapi import UploadFile
from PIL import Image
import io
from app.schemas import AddImagesResponse, DuplicateImage
from app.services import PineconeService, ImageProcessor
from app.utils import decode_base64_image


class ImageService:
    def __init__(self, pinecone_service: PineconeService, image_processor: ImageProcessor):
        self.pinecone_service = pinecone_service
        self.image_processor = image_processor

    async def process_images(self, files: List[UploadFile], base64_images: List[str], urls: List[str]) -> AddImagesResponse:
        request_id = str(uuid.uuid4())
        added_count = 0
        embeddings_to_add = []

        # Process Multipart/Form-Data files
        if files:
            for file in files:
                if file.content_type not in ['image/jpeg', 'image/png']:
                    continue
                contents = await file.read()
                if len(contents) > 10 * 1024 * 1024:
                    continue
                try:
                    image = Image.open(io.BytesIO(contents)).convert('RGB')
                    embedding = self.image_processor.get_embedding(image)
                    image_id = str(uuid.uuid4())
                    embeddings_to_add.append({
                        'id': image_id,
                        'values': embedding,
                        'metadata': {'request_id': request_id}
                    })
                    added_count += 1
                except Exception:
                    continue

        # Process Base64 images
        if base64_images:
            for b64_str in base64_images:
                try:
                    image = decode_base64_image(b64_str)
                    embedding = self.image_processor.get_embedding(image)
                    image_id = str(uuid.uuid4())
                    embeddings_to_add.append({
                        'id': image_id,
                        'values': embedding,
                        'metadata': {'request_id': request_id}
                    })
                    added_count += 1
                except Exception:
                    continue

        # Process URLs
        if urls:
            for url in urls:
                try:
                    image = self.image_processor.load_image_from_url(url)
                    embedding = self.image_processor.get_embedding(image)
                    image_id = str(uuid.uuid4())
                    embeddings_to_add.append({
                        'id': image_id,
                        'values': embedding,
                        'metadata': {'request_id': request_id}
                    })
                    added_count += 1
                except Exception:
                    continue

        if embeddings_to_add:
            self.pinecone_service.add_embeddings(embeddings_to_add)

        return AddImagesResponse(request_id=request_id, added_count=added_count)

    def find_duplicates(self, request_id: str) -> List[DuplicateImage]:
        vectors = self.pinecone_service.get_vectors_by_request_id(request_id)
        if not vectors:
            return []

        duplicates = []
        for vector in vectors:
            duplicate_matches = self.pinecone_service.query_duplicates(vector['values'])
            for match in duplicate_matches:
                if match['id'] != vector['id']:
                    duplicates.append(DuplicateImage(
                        image_id=match['id'],
                        score=match['score'],
                        metadata=match['metadata']
                    ))

        return duplicates
