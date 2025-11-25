from fastapi import HTTPException
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.core.schenma.reponse_schenma import * 
from app.core.vector_strore.base_vectorDB import VectorStore
import uuid


class QdrantService(VectorStore):
    def __init__(
        self, 
        embedding_dims,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        distance: Distance = Distance.COSINE
        ):
        super().__init__(embedding_dims = embedding_dims)
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.distance_metric = distance
    
    async def create_collection(self):
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dims,
                    distance=self.distance_metric
                )
            )
    
    def validate_embeding(self, embeding: List[float]):
        if len(embeding) != self.embedding_dims:
            raise HTTPException(
                status_code=400,
                detail=f"Embeding size must be{self.embedding_dims}, got {len(embeding)}"
            )
    
    async def insert_embeding(self, doc_request: DocumentEbedingRequest) -> RequestResult:
        self.validate_embeding(doc_request.embeding)
        
        if await self.get_point_id(doc_request.doc_id):
            raise HTTPException(
                status_code=409,
                detail=f"Document with id {doc_request.doc_id} already exists."
            )
            
        payload = {
            "doc_id": doc_request.doc_id,
            "content": doc_request.context,
            "chunk_id": doc_request.chunk_id,
            "total_chunks": doc_request.total_chunks,
            # "metadata": doc_request.metadata
        }
        
        point = PointStruct(
            id = str(uuid.uuid4()),
            vector = doc_request.embeding,
            payload = payload
        )
        
        await self.client.upsert(collection_name=self.collection_name, points=[point])

        return RequestResult(
            request_id=str(uuid.uuid4()),
            status=ResponseStatus.COMPLETED,
            request_type=RequestType.INSERT
        )
        
    async def get_point_id(self, doc_id: str, limit: int = 1):
        payload_filter = Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        )
        
        result = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter= payload_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        return result[0][0] if result[0] else None
    
    async def delete_embeding(self, doc_ids: List[str]) -> DeleteResponse:
        doc_ids =list(set(doc_ids))  # Remove duplicate
        point_ids_to_delete = []
        failed_ids = []
        
        for doc_id in doc_ids:
            point = await self.get_point_id(doc_id)
            if point:
                point_ids_to_delete.append(point)
            else:
                failed_ids.append(doc_id)
        
        if not point_ids_to_delete:
            return DeleteResponse(
                deleted_ids=[],
                faild_ids=failed_ids,
                message="No matching documents found for delete"
            )
        
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids_to_delete
        )
        
        delete_ids = [doc_id for doc_id in doc_ids if doc_id not in failed_ids]
        
        return DeleteResponse(
            deleted_ids=delete_ids,
            faild_ids=failed_ids,
            message=f"Delete {len(delete_ids)} documents, failed {len(failed_ids)}"
        )
    
    async def delete_all_data(self):
        try:
            if not await self.client.collection_exists(self.collection_name):
                return DeleteAllResponse(
                    sucess=False,
                    message="Collection does not exist."
                )
            await self.client.delete_collection(self.collection_name)
            await self.create_collection()
            
            return DeleteAllResponse(
                sucess=True,
                message="All data in the collection has been deleted and collection created"
            )
        except Exception as e:
            return DeleteAllResponse(
                sucess=False,
                message=f"Failed to delete all data: {str(e)}"
            )
    
    async def delete_poit(self, doc_id: str) -> RequestResult:
        point = await self.get_point_id(doc_id)
        if not point :
            raise HTTPException(
                status_code=404,
                detail=f"Document with id {doc_id} not found"
            )
            
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[point.id]
        )
        
        return RequestResult(
            request_id=str(uuid.uuid4()),
            status=ResponseStatus.COMPLETED,
            request_type=RequestType.DELETE,
            data=point.payload
        )
    
    async def retrieve_points(self, embedding: List[float], similarity_top_k: int = 3) -> List[RetrivalResuult]:
        self.validate_embeding(embedding)

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=similarity_top_k
        )
        
        return [RetrivalResuult(scorce=result.score, payload=result.payload)
                for result in results
        ]
        
    async def batch_retrieve(self, embeddings: List[List[float]], top_k: int = 3) -> List[List[RetrivalResuult]]:
        for emb in embeddings:
            self.validate_embeding(emb)
        
        requests = [{"vector": vector, "limit": top_k} for vector in embeddings]
        
        results = await self.client.search_batch(
            collection_name=self.collection_name,
            requests=requests
        )
        
        return [
            [
                RetrivalResuult(
                    scorce=res.score,
                    payload=res.payload if res.payload is not None else {}
                ) for res in group
            ]
            for group in results 
        ]
    
    async def get_all_documents(self) -> List[Dict]:
        results = []
        collections_response = await self.client.get_collection()
        collections = collections_response.collections 
        
        for collection in collections:
            offset = None
            while True:
                points, next_page = await self.client.scroll(
                    collection_name=collection.name,
                    offset=offset,
                    limit=100,
                    with_payload=True,
                    with_vectors=False
                )
                for point in points:
                    payload = point.payload or {}
                    text = payload.get("context", "") or payload.get("text", "")
                    results.append({
                        "id": point.id,
                        "text": text
                    })
                if next_page is None:
                    break
                offset = next_page
        
        return results
    
    
