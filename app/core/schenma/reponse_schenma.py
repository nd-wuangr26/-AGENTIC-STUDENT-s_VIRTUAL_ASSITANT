from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from strenum import StrEnum

class DocumentEbedingRequest(BaseModel):
    doc_id: str
    context: str
    embeding: List[float]
    chunk_id: Optional[str] = "0"
    total_chunks: Optional[int] = 1

class RequestResult(BaseModel):
    request_id: str
    status: str
    request_type: str
    data: Optional[Any] = None

class RetrivalResuult(BaseModel):
    scorce: float
    payload: dict

class BatchQueryRequest(BaseModel):
    queries: List[str]
    top_k: int = 3
    search_method: str = "Hybrid" # Vetor, keyword, hybrid
    alpha: float = 0.5 # Dung cho Hybrid
    
class DeleteRequests(BaseModel):
    ids: List[str]
    
class DeleteResponse(BaseModel):
    message: str
    deleted_ids: List[str]
    faild_ids: List[str]
    
class UploadResponse(BaseModel):
    message: str
    count_chunk: int
    ids: List[str]
    
class DeleteAllResponse(BaseModel):
    sucess: bool
    message: str
    
class ResponseStatus(StrEnum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
class RequestType(StrEnum):
    QUERY = "QUERY"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
# ======= Request Schenma =======
class Message(BaseModel):
    role: str
    content: str
    
class QueryPayload(BaseModel):
    data: List[Message]

# Simple schema for frontend chat interface
class QuestionRequest(BaseModel):
    question: str