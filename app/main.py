import uuid

from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from app.schemas import AddImagesResponse, SearchDuplicatesResponse, DuplicateImage
from app.services import ImageProcessor
from app.services import PineconeService
from app.utils import decode_base64_image
import io
import os

app = FastAPI(title="Image Duplicate Detection Service")

# Initialize services
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
pinecone_service = PineconeService(api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME)
image_processor = ImageProcessor(device='cpu')


@app.post("/images", response_model=AddImagesResponse)
async def add_images(
        files: List[UploadFile] = File(None),
        base64_images: List[str] = None,
        urls: List[str] = None
):
    if not (files or base64_images or urls):
        raise HTTPException(status_code=400, detail="No images provided")

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
                embedding = image_processor.get_embedding(image)
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
                embedding = image_processor.get_embedding(image)
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
                image = image_processor.load_image_from_url(url)
                embedding = image_processor.get_embedding(image)
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
        pinecone_service.add_embeddings(embeddings_to_add)

    return AddImagesResponse(request_id=request_id, added_count=added_count)


@app.get("/duplicates/{request_id}", response_model=SearchDuplicatesResponse)
def search_duplicates(request_id: str):
    vectors = pinecone_service.get_vectors_by_request_id(request_id)
    if not vectors:
        return SearchDuplicatesResponse(message="No duplicates found or invalid request_id.")

    duplicates = []
    for vector in vectors:
        duplicate_matches = pinecone_service.query_duplicates(vector['values'])
        for match in duplicate_matches:
            if match['id'] != vector['id']:
                duplicates.append(DuplicateImage(
                    image_id=match['id'],
                    score=match['score'],
                    metadata=match['metadata']
                ))

    if duplicates:
        return SearchDuplicatesResponse(duplicates=duplicates)
    else:
        return SearchDuplicatesResponse(message="No duplicates found.")
