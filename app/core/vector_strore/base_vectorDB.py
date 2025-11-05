from typing import List
from app.core.schenma.reponse_schenma import DocumentEbedingRequest, RequestResult, RetrivalResuult

class VectorStore:
    def __init__(self, embedding_dims: int):
        self.embedding_dims = embedding_dims
        
    async def insert_db(self, doc_request: DocumentEbedingRequest) -> RequestResult:
        """
        Insert new document embedding into the vector store.
        """
        raise NotImplementedError()
    
    async def delete_point(self, doc_id: str) -> RetrivalResuult:
        """
        Delete a document's vector based on its doc_id.
        """
        raise NotImplementedError()
    
    async def retrival_db(self, embeding: List[float], similaty_top_k: int = 3) -> List[RetrivalResuult]:
        """
        Retrieve top-k similar documents based on the input embedding.
        """
        raise NotImplementedError