import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
from app.core.config.config import *
from langchain_huggingface import HuggingFaceEmbeddings
from app.startup.startup import init_qdrant_service, get_qdrant_service
import uuid
from app.core.schenma.reponse_schenma import DocumentEbedingRequest, RequestResult, ResponseStatus
from agentscope.embedding import OpenAITextEmbedding
import asyncio
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY_API = os.getenv("OPENAI_API_KEY")
init_qdrant_service()
qdrant_service = get_qdrant_service()

class SaveVectorDB():
    def __init__(self, model_name: str = MODEL_NAME_EMBEDDING, file_path: str = DOCUMENT_PATH):
        self.embed_model_id = model_name
        self.file_path = file_path
        self.embedding = OpenAITextEmbedding(api_key=OPENAI_KEY_API, model_name="text-embedding-3-small", dimensions=EMBEDDING_DIMS)

        
    def load_docling(self):
        """Load documents from Docling."""
        EXPORT_TYPE = ExportType.DOC_CHUNKS
        loader = DoclingLoader(file_path=self.file_path,
                               export_type=EXPORT_TYPE,
                               chunker=HybridChunker(tokenizer=self.embed_model_id))
        documents = loader.load()
        return documents
    
    async def save_document(self, texts) -> RequestResult:
        datetime_object = datetime.datetime.now()
        # Save vector DB
        for text in texts:
            embedding = self.embeddings.embed_documents([text.page_content])[0]  # Lấy phần tử đầu
            doc = DocumentEbedingRequest(
                chunk_id=str(uuid.uuid4()),
                total_chunks=text.page_content,
                embeding=embedding
            )
            await qdrant_service.insert_embeding(doc_request=doc)

    async def save_document_openai(self, texts) -> RequestResult:
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_KEY_API)

        # Save vector DB
        for i, text in enumerate(texts):
            try:
                # Truncate content to avoid token limit (approx 8192 tokens)
                # 1 token ~= 4 chars, so 30000 chars is safe upper bound usually, but let's go with 25000
                content_to_embed = text.page_content[:25000]
                
                # Call OpenAI directly to avoid agentscope caching issues
                response = await client.embeddings.create(
                    input=content_to_embed,
                    model="text-embedding-3-small",
                    dimensions=EMBEDDING_DIMS
                )
                embedding = response.data[0].embedding
                print(f"DEBUG: Chunk {i} embedding length: {len(embedding)}")

                doc = DocumentEbedingRequest(
                    doc_id=str(uuid.uuid4()),
                    context=text.page_content, # Store full content
                    embeding=embedding,
                    chunk_id=str(i),
                    total_chunks=len(texts)
                )
                await qdrant_service.insert_embeding(doc_request=doc)
                print(f"Saved chunk {i}/{len(texts)}")
            except Exception as e:
                print(f"Error saving chunk {i}: {e}")

async def main():
    # Re-create collection to clear old incompatible data
    await qdrant_service.delete_all_data()
    # Ensure collection exists
    await qdrant_service.create_collection()
    
    chunker = SaveVectorDB()
    docs = chunker.load_docling()
    print(f"Mẫu chunk: {docs[:1]}")
    await chunker.save_document_openai(docs)

if __name__ == "__main__":
    asyncio.run(main())
