from fastapi import FastAPI
from app.routers import image_router

app = FastAPI(title="Image Duplicate Detection Service")

app.include_router(image_router)
