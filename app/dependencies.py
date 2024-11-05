from fastapi import Depends

from app.services import ImageProcessor, PineconeService, ImageService
from app.config import settings


def get_pinecone_service():
    return PineconeService(api_key=settings.pinecone_api_key, index_name=settings.pinecone_index_name)


def get_image_processor():
    return ImageProcessor(device='cpu')


def get_image_service(pinecone_service: PineconeService = Depends(get_pinecone_service),
                      image_processor: ImageProcessor = Depends(get_image_processor)):
    return ImageService(pinecone_service=pinecone_service, image_processor=image_processor)
