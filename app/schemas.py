from typing import List, Optional
from pydantic import BaseModel


class AddImagesResponse(BaseModel):
    request_id: str
    added_count: int


class DuplicateImage(BaseModel):
    image_id: str
    score: float
    metadata: dict


class SearchDuplicatesResponse(BaseModel):
    duplicates: Optional[List[DuplicateImage]] = None
    message: Optional[str] = None
