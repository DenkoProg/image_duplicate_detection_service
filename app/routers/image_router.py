# app/routers/image_router.py
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.schemas import AddImagesResponse, SearchDuplicatesResponse, DuplicateImage
from app.services import ImageService
from app.dependencies import get_image_service

image_router = APIRouter()


@image_router.post("/images", response_model=AddImagesResponse)
async def add_images(
        files: List[UploadFile] = File(None),
        base64_images: List[str] = None,
        urls: List[str] = None,
        image_service: ImageService = Depends(get_image_service)
):
    if not (files or base64_images or urls):
        raise HTTPException(status_code=400, detail="No images provided")

    response = await image_service.process_images(files, base64_images, urls)
    return response


@image_router.get("/duplicates/{request_id}", response_model=SearchDuplicatesResponse)
def search_duplicates(
        request_id: str,
        image_service: ImageService = Depends(get_image_service)
):
    duplicates = image_service.find_duplicates(request_id)
    if duplicates:
        return SearchDuplicatesResponse(duplicates=duplicates)
    else:
        return SearchDuplicatesResponse(message="No duplicates found.")
