from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.rag.agentic import app as agentic_router
import time
from app.startup.startup import init_qdrant_service, get_qdrant_service


# tag
tags_metadata = [
    {
        "name": "RAG Basic",
        "description": "Basic RAG operations",
    },
]

app = FastAPI(
    title="AGENTIC - RAG API",
    description="agentic RAG API with Qdrant Vector Database",
    version="2.0.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust as needed
    allow_headers=["*"],  # Allows all headers, adjust as needed
)   

app.include_router(agentic_router, prefix="/api/generate", tags=["RAG Basic"])

@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize resources if needed.
    """
    start = time.perf_counter()
    print("Starting up the application...")
    
    # Simulate some startup tasks
    init_qdrant_service()
    end = time.perf_counter()
    print(f"Application started in {end - start:.2f} seconds.")
    
    # Optionally, you can initialize other services or resources here
    qdrant_service = get_qdrant_service()
    print(f"Qdrant service initialized: {qdrant_service}")
    # Here you can add any startup logic, like connecting to a database
    print("Application startup: initializing resources...")

