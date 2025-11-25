from pathlib import Path
import sys

# Lên 3 cấp từ file hiện tại để đến thư mục chứa "app"
project_root = Path(__file__).resolve().parents[3]

# Thêm vào sys.path nếu chưa có
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))



import asyncio
import json
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.rag import (
    TextReader,
    SimpleKnowledge,
    QdrantStore,
    Document,
    ImageReader,
)
from agentscope.embedding import OpenAITextEmbedding
from agentscope.formatter import OpenAIChatFormatter
from agentscope.tool import Toolkit
from app.core.config.config import *
from app.core.embeding.embeddings import Embedding
from app.core.schenma.reponse_schenma import QueryPayload, QuestionRequest
from app.core.CRUD_Mysql.base_mysql import *
from fastapi import APIRouter
from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_KEY_API = os.getenv("OPENAI_API_KEY")
qdrant_url = "http://localhost:6333"
LLM_KEY = os.getenv('Gemini_api_key')

app = APIRouter()



OpenAI_embedding = OpenAITextEmbedding(
    api_key=OPENAI_KEY_API,
    model_name="text-embedding-3-small",
)

# Shared chat model/formatter for agents
chat_model = OpenAIChatModel(
    api_key=OPENAI_KEY_API,
    model_name="gpt-4o-mini",
)
chat_formatter = OpenAIChatFormatter()

# ---------------------------
# MySQL toolset (MCP-style tools)
# ---------------------------

def build_mysql_toolkit() -> Toolkit:
    return Toolkit.from_functions(
        [
            tool_add_student,
            tool_update_booking,
            tool_remove_student,
            tool_get_student_info,
            tool_list_available_rooms,
        ],
        descriptions={
            "tool_add_student": "Create a dorm booking: args (student_id:int, room_id:int, start_date:str 'YYYY-MM-DD', end_date:str 'YYYY-MM-DD').",
            "tool_update_booking": "Update booking status: args (booking_id:int, status:str one of PENDING/APPROVED/REJECTED/CANCELLED).",
            "tool_delete_booking": "Delete a booking by id: args (booking_id:int).",
            "tool_get_booking": "Get booking details by id: args (booking_id:int).",
            "tool_list_available_rooms": "List rooms that are currently available for booking.",
        },
    )


# ---------------------------
# Agents
# ---------------------------
def make_rag_agent():
    knowledge = SimpleKnowledge(
        embedding_model=OpenAI_embedding,
        embedding_store=QdrantStore(
            location=qdrant_url,
            collection_name="documents",
            # OpenAI text-embedding-3-small returns 1536 dims
            dimensions=EMBEDDING_DIMS,
        ),
    )
    return ReActAgent(
        name="RAG_AGENT",
        sys_prompt="Bạn là trợ lý RAG. Trả lời chính xác dựa trên kho tri thức đã lập chỉ mục.",
        model=chat_model,
        formatter=chat_formatter,
        knowledge=knowledge,
    )


def make_db_agent():
    toolkit = build_mysql_toolkit()
    return ReActAgent(
        name="DB_AGENT",
        sys_prompt=(
            "Bạn là trợ lý quản lý ký túc xá. "
            "Sử dụng tool để thực hiện CRUD trên MySQL cho các yêu cầu: "
            "tạo đặt phòng, cập nhật trạng thái, xóa, tra cứu đặt phòng và liệt kê phòng trống. "
            "Luôn gọi tool phù hợp dựa trên yêu cầu của sinh viên và trả về kết quả ngắn gọn."
        ),
        model=chat_model,
        formatter=chat_formatter,
        tools=toolkit,
    )


async def route_intent(user_text: str) -> str:
    """
    Return one of: 'RAG', 'DB'
    """
    import openai
    client = openai.AsyncOpenAI(api_key=OPENAI_KEY_API)
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là bộ định tuyến. Nhiệm vụ DUY NHẤT là phân loại yêu cầu.\n- Nếu câu hỏi tra cứu kiến thức, tài liệu, hoặc hỏi thông tin chung: trả về RAG\n- Nếu yêu cầu đặt phòng, kiểm tra phòng trống, hoặc thao tác dữ liệu: trả về DB\nKHÔNG trả lời câu hỏi. KHÔNG giải thích. CHỈ trả về đúng 1 từ: RAG hoặc DB."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    
    text = response.choices[0].message.content.strip().upper()
    if "DB" in text:
        return "DB"
    return "RAG"


async def query_rag(user_text: str) -> str:
    """Query RAG using Qdrant and OpenAI"""
    import openai
    client = openai.AsyncOpenAI(api_key=OPENAI_KEY_API)
    
    # Get embedding for query
    emb_response = await client.embeddings.create(
        input=user_text,
        model="text-embedding-3-small",
        dimensions=EMBEDDING_DIMS
    )
    query_embedding = emb_response.data[0].embedding
    
    # Search Qdrant
    from qdrant_client import AsyncQdrantClient
    qdrant = AsyncQdrantClient(url=qdrant_url)
    
    search_results = await qdrant.query_points(
        collection_name="documents",
        query=query_embedding,
        limit=3
    )
    
    # Build context from results
    points = search_results.points if hasattr(search_results, 'points') else search_results
    context = "\n\n".join([
        f"[Tài liệu {i+1}]: {point.payload.get('context', point.payload.get('content', ''))}"
        for i, point in enumerate(points)
    ])
    
    # Generate answer
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Bạn là trợ lý RAG. Trả lời chính xác dựa trên kho tri thức đã lập chỉ mục.\n\nTài liệu tham khảo:\n{context}"},
            {"role": "user", "content": user_text}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content


async def query_db(user_text: str) -> str:
    """Query DB using tools"""
    import openai
    client = openai.AsyncOpenAI(api_key=OPENAI_KEY_API)
    
    # Define tools for OpenAI function calling
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_available_rooms",
                "description": "Liệt kê các phòng ký túc xá còn chỗ trống",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_student",
                "description": "Thêm sinh viên vào phòng ký túc xá. Tự động kiểm tra phòng đã đủ người chưa.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Mã số sinh viên"},
                        "ten": {"type": "string", "description": "Tên sinh viên"},
                        "nam_sinh": {"type": "integer", "description": "Năm sinh"},
                        "room_id": {"type": "string", "description": "Mã phòng (ví dụ: A100, B201)"}
                    },
                    "required": ["mssv", "ten", "nam_sinh", "room_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_student_info",
                "description": "Lấy thông tin sinh viên theo MSSV",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Mã số sinh viên"}
                    },
                    "required": ["mssv"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_room_info",
                "description": "Lấy thông tin phòng và danh sách sinh viên trong phòng",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string", "description": "Mã phòng (ví dụ: A100, B201)"}
                    },
                    "required": ["room_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_student",
                "description": "Xóa sinh viên khỏi ký túc xá",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Mã số sinh viên"}
                    },
                    "required": ["mssv"]
                }
            }
        }
    ]
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý quản lý ký túc xá. Sử dụng tool để thực hiện CRUD trên MySQL."},
            {"role": "user", "content": user_text}
        ],
        tools=tools,
        temperature=0
    )
    
    message = response.choices[0].message
    
    # If tool call is requested
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        
        import json
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute the tool
        try:
            if function_name == "list_available_rooms":
                from app.core.CRUD_Mysql.base_mysql import tool_list_available_rooms
                result = tool_list_available_rooms()
            elif function_name == "add_student":
                from app.core.CRUD_Mysql.base_mysql import tool_add_student
                result = tool_add_student(**arguments)
            elif function_name == "get_student_info":
                from app.core.CRUD_Mysql.base_mysql import tool_get_student_info
                result = tool_get_student_info(**arguments)
            elif function_name == "get_room_info":
                from app.core.CRUD_Mysql.base_mysql import tool_get_room_info
                result = tool_get_room_info(**arguments)
            elif function_name == "remove_student":
                from app.core.CRUD_Mysql.base_mysql import tool_remove_student
                result = tool_remove_student(**arguments)
            else:
                result = {"error": "Unknown function"}
        except Exception as e:
            result = {
                "error": f"Database error: {str(e)}",
                "message": "MySQL connection failed. Please check your database configuration in .env file."
            }
        
        from app.core.llm.geminiLLM import GeminiLLM
        gemini_llm = GeminiLLM(api_key=os.getenv("GEMMINI_API_KEY"))
        result = gemini_llm.generate_content(
            f"Hãy trình bày kết quả sau đây một cách ngắn gọn và dễ hiểu cho sinh viên ký túc xá:\n{json.dumps(result, ensure_ascii=False)}"
        )
        
        return result
    
    return message.content or "Không thể xử lý yêu cầu."


@app.post("/search")
async def build_knowledge_base(payload: QuestionRequest):
    """
    Route input to either RAG agent (Qdrant) or DB agent (MySQL CRUD) based on intent.
    """
    user_text = payload.question if payload else ""
    if not user_text:
        return {"ok": False, "error": "Empty input"}

    try:
        route = await route_intent(user_text)
        
        if route == "DB":
            answer = await query_db(user_text)
        else:
            answer = await query_rag(user_text)
        
        return {"ok": True, "route": route, "answer": answer}
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}

