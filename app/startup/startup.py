from RAG_QrandtDB.app.db.qdrant_service import QdrantService, Distance

from RAG_QrandtDB.app.core.config.config import (EMBEDDING_DIMS)



qdrant_service = None

def init_qdrant_service() -> QdrantService:
    global qdrant_service
    qdrant_service = QdrantService(
                                   embedding_dims = EMBEDDING_DIMS,
                                   distance = Distance.COSINE)

def get_qdrant_service() -> QdrantService:
    return qdrant_service