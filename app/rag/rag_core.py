from app.core.embeding.embeddings import Embedding
from app.core.llm.geminiLLM import GeminiLLM
from app.core.re_renk.core import ReRank
from app.core.schenma.reponse_schenma import QueryPayload
from app.db.qdrant_service import QdrantService
from app.reflection.core import Reflection
from app.sematic_router.sematic_route import SematicRouter
from app.sematic_router.route import Route
from app.sematic_router.sample import productSample, chitchatSample
from app.core.config.config import *
from fastapi import APIRouter
from dotenv import load_dotenv
import os

load_dotenv()

rag_core = APIRouter()

LLM_KEY = os.getenv('Gemini_api_key')

# --- Semantic Router Setup --- #

PRODUCT_ROUTE_NAME = 'products' # define products route name
CHITCHAT_ROUTE_NAME = 'chitchat'

Embeding = Embedding(name=MODEL_NAME_EMBEDDING)
productRoute = Route(name=PRODUCT_ROUTE_NAME, samples=productSample)
chitchatRoute = Route(name=CHITCHAT_ROUTE_NAME, samples=chitchatSample)
semanticRouter = SematicRouter(Embeding, routes=[productRoute, chitchatRoute])

# --- End Semantic Router Setup --- #

# --- Set up LLMs --- #

LLM = GeminiLLM(api_key=LLM_KEY)

# --- End Set up LLMs --- #

# --- Relection Setup --- #

reflection = Reflection(llm=LLM)

# --- End Reflection Setup --- #

# ----- Set up Qrandt ------- #

qdrant_service = QdrantService(embedding_dims=EMBEDDING_DIMS)

# ------ End Qrandt set up -------#


# Initialize RAG
reranker = ReRank(model_name="BAAI/bge-reranker-v2-m3")
def process_query(query):
    return query.lower()

@rag_core.post("/search")
async def handle_query(payload: QueryPayload):
    data = [{
        "role": m.role,
        "parts": [{"text": m.content}]
    } for m in payload.data]

    print(f"Received data: {data}")

    # Step 1: Reflect query
    query = reflection(data)
    print(f"Reflected query: {query}")
    query_processed = process_query(query)
    # Step 2: Semantic route
    guided_score, guided_route = semanticRouter.guide(query_processed)
    print(f"Guided route: {guided_route}, Score: {guided_score}")

    if guided_route == PRODUCT_ROUTE_NAME:
        # Step 3: vector search từ RAG (Qdrant)
        query_embedding = Embeding.encode([query])
        print("len", len(query_embedding))
        retrieved = await qdrant_service.retrieve_points(
            embedding=query_embedding,
            similarity_top_k=5
        )
        passages = [r.payload.get("content", "") for r in retrieved]

        # Step 4: rerank
        scores, ranked_passages = reranker(query, passages)
        print(f"Ranked passages: {ranked_passages}")
        print(f"Scores: {scores}")
        source_information = "\n".join([f"{i+1}. {p}" for i, p in enumerate(ranked_passages)])

        # Step 5: tạo prompt
        combined_prompt = (
            f"Hãy trở thành chuyên gia tư vấn tuyển sinh đa ngành nghề của trường Đại học Kỹ thuật Công nghiệp - Đại học Thái Nguyên.\n"
            f"Câu hỏi của khách hàng: {query}\n"
            f"Dựa vào các thông tin sau, hãy trả lời:\n{source_information}"
        )
        data.append({
            "role": "user",
            "parts": [{"text": combined_prompt}]
        })

        # Step 6: Gọi LLM (ví dụ Together)
        response = LLM.generate_content(data)
        final_response = response
    else:
        # Chitchat - chỉ cần dùng LLM trả lời
        print("Guide to LLMs")
        response = LLM.generate_content(data)
        final_response = response

    return {
        "content": final_response,
        "role": "assistant"
    }