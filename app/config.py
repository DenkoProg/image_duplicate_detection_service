import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME")


settings = Settings()
