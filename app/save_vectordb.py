from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
from core.config.config import *
from langchain_huggingface import HuggingFaceEmbeddings
from startup.startup import init_qdrant_service, get_qdrant_service
import uuid
from core.schenma.reponse_schenma import DocumentEbedingRequest, RequestResult, ResponseStatus
import asyncio
import datetime


init_qdrant_service()
qdrant_service = get_qdrant_service()

class SaveVectorDB():
    def __init__(self, model_name: str = MODEL_NAME_EMBEDDING, file_path: str = DOCUMENT_PATH):
        self.embed_model_id = model_name
        self.file_path = file_path
        self.embeddings = HuggingFaceEmbeddings(model_name = model_name)
        
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
                doc_id=str(uuid.uuid4()),
                context=text.page_content,
                embeding=embedding,
                metadata={
                    "source": str(self.file_path),
                    "created": str(datetime_object)
                }
            )
            await qdrant_service.insert_embeding(doc_request=doc)

async def main():
    await qdrant_service.create_collection()
    chunker = SaveVectorDB()
    docs = chunker.load_docling()
    print(f"Mẫu chunk: {docs[:1]}")
    await chunker.save_document(docs)

if __name__ == "__main__":
    asyncio.run(main())
