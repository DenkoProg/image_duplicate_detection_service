import pinecone
from typing import List, Dict
from pinecone import ServerlessSpec


class PineconeService:
    def __init__(self, api_key: str, index_name: str = 'image-duplicates'):
        pc = pinecone.Pinecone(api_key=api_key)
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=2048,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1',
                )
            )
        self.index = pc.Index(index_name)

    def add_embeddings(self, embeddings: List[Dict]):
        # embeddings: List of {'id': str, 'values': List[float], 'metadata': Dict}
        self.index.upsert(vectors=embeddings)

    def query_duplicates(self, vector: List[float], top_k: int = 5, threshold: float = 0.9) -> List[Dict]:
        results = self.index.query(vector=[vector], top_k=top_k, include_metadata=True, include_values=True)
        duplicates = []
        for match in results['matches']:
            if match['score'] >= threshold:
                duplicates.append(match)
        return duplicates

    def get_vectors_by_request_id(self, request_id: str) -> List[Dict]:
        filter = {'request_id': request_id}
        results = self.index.query(vector=[0] * 2048, filter=filter, top_k=1000, include_metadata=True, include_values=True)
        return results['matches']
