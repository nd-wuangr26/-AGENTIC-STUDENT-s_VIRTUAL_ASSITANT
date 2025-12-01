from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.rag.agentic import app as agentic_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.chat import router as chat_router
import time
from app.startup.startup import init_qdrant_service, get_qdrant_service
from app.core.services.mysql_service import init_mysql_service, get_mysql_service


# tag
tags_metadata = [
    {
        "name": "RAG Basic",
        "description": "Basic RAG operations",
    },
    {
        "name": "Authentication",
        "description": "User authentication and authorization",
    },
    {
        "name": "Admin Dashboard",
        "description": "Admin dashboard operations (requires admin role)",
    },
    {
        "name": "Chat History",
        "description": "Chat history management (requires authentication)",
    },
]

app = FastAPI(
    title="AGENTIC - RAG API",
    description="agentic RAG API with Qdrant Vector Database and Admin Dashboard",
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

# Include routers
app.include_router(agentic_router, prefix="/api/generate", tags=["RAG Basic"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin Dashboard"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat History"])

@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize resources if needed.
    """
    start = time.perf_counter()
    print("Starting up the application...")
    
    # Initialize Qdrant service
    init_qdrant_service()
    qdrant_service = get_qdrant_service()
    print(f"Qdrant service initialized: {qdrant_service}")
    
    # Initialize MySQL service
    await init_mysql_service()
    mysql_service = get_mysql_service()
    print(f"MySQL service initialized: {mysql_service}")
    
    end = time.perf_counter()
    print(f"Application started in {end - start:.2f} seconds.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event to cleanup resources.
    """
    print("Shutting down the application...")
    mysql_service = get_mysql_service()
    await mysql_service.close_pool()
    print("MySQL connection pool closed.")
