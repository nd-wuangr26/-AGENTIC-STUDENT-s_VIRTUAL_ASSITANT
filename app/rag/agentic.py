"""
LangGraph-based Agentic RAG System
Implements multi-agent system with routing, RAG, MySQL, and Web Search capabilities
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
import json
import openai
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# FastAPI
from fastapi import APIRouter
from pydantic import BaseModel

# Local imports
from app.core.mcp.mysql_mcp_server import get_mcp_server
from app.core.config.config import EMBEDDING_DIMS

# Schema imports
from app.core.schenma.reponse_schenma import *

# Qdrant imports
from app.db.qdrant_service import QdrantService


load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Initialize router
app = APIRouter()


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State for the agent graph"""
    messages: list
    question: str
    route: str  # 'rag', 'database', 'web_search'
    context: str
    answer: str
    error: str


# ============================================================================
# Tools Definition
# ============================================================================

# MySQL Tools via MCP
mcp_server = get_mcp_server()

@tool
def list_available_rooms() -> dict:
    """List all available dormitory rooms with vacancy information"""
    return mcp_server.list_available_rooms()

@tool
def add_student(mssv: str, ten: str, nam_sinh: int, room_id: str) -> dict:
    """
    Add a new student to a dormitory room
    
    Args:
        mssv: Student ID
        ten: Student name
        nam_sinh: Birth year
        room_id: Room ID (e.g., A100, B201)
    """
    return mcp_server.add_student(mssv, ten, nam_sinh, room_id)

@tool
def get_student_info(mssv: str) -> dict:
    """
    Get detailed information about a student by their ID
    
    Args:
        mssv: Student ID
    """
    return mcp_server.get_student_info(mssv)

@tool
def get_room_info(room_id: str) -> dict:
    """
    Get room information and list of students in the room
    
    Args:
        room_id: Room ID (e.g., A100, B201)
    """
    return mcp_server.get_room_info(room_id)

@tool
def remove_student(mssv: str) -> dict:
    """
    Remove a student from the dormitory
    
    Args:
        mssv: Student ID
    """
    return mcp_server.remove_student(mssv)

# Web Search Tool
@tool
def web_search(query: str) -> str:
    """
    Search the web using Google Search via Serper API for current information
    
    Args:
        query: Search query
    """
    try:
        if not SERPER_API_KEY:
            return "Web search unavailable: SERPER_API_KEY not configured"
        
        search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
        results = search.run(query)
        return results
    except Exception as e:
        return f"Web search failed: {str(e)}"


# Database tools list
database_tools = [
    list_available_rooms,
    add_student,
    get_student_info,
    get_room_info,
    remove_student
]

# Web search tools list
web_search_tools = [web_search]


# ============================================================================
# LLM Setup
# ============================================================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# LLM with database tools
llm_with_db_tools = llm.bind_tools(database_tools)

# LLM with web search tools
llm_with_web_tools = llm.bind_tools(web_search_tools)


# ============================================================================
# Vector Store Setup (Using QdrantService)
# ============================================================================
# Note: QdrantService is now used directly in rag_agent function


# ============================================================================
# Node Functions
# ============================================================================

def route_question(state: AgentState) -> AgentState:
    """Route the question to appropriate agent"""
    question = state["question"]
    
    # Use LLM to classify intent
    router_prompt = f"""Classify the following question into ONE category:
        - 'database': Questions about dormitory rooms, students, bookings, or any database operations
        - 'rag': Questions about general knowledge, documents, or information from knowledge base
        - 'web_search': Questions requiring current information, news, or real-time data

        Question: {question}

        Respond with ONLY one word: database, rag, or web_search"""
    
    messages = [SystemMessage(content=router_prompt)]
    response = llm.invoke(messages)
    
    route = response.content.strip().lower()
    
    print(f"Routing decision: {route}")
    
    # Validate route
    if route not in ['database', 'rag', 'web_search']:
        route = 'rag'  # Default to RAG
    
    state["route"] = route
    state["messages"] = [HumanMessage(content=question)]
    
    return state


async def rag_agent(state: AgentState) -> AgentState:
    """RAG agent - retrieves from knowledge base and generates answer"""
    question = state["question"]
    
    try:
        print(f"RAG Agent processing: {question}")
        
        # Initialize QdrantService
        qdrant_service = QdrantService(
            embedding_dims=EMBEDDING_DIMS,
            host="localhost",
            port=6333,
            collection_name="documents"
        )
        
        print("QdrantService initialized")
        
        # Create embedding for the question using OpenAI
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        emb_response = await client.embeddings.create(
            input=question,
            model="text-embedding-3-small",
            dimensions=EMBEDDING_DIMS
        )
        query_embedding = emb_response.data[0].embedding
        
        print(f"Query embedding created (dim: {len(query_embedding)})")
        
        # Retrieve relevant documents using QdrantService
        results = await qdrant_service.retrieve_points(
            embedding=query_embedding
        )
        
        print(f"Retrieved {len(results)} documents")
        
        # Build context from results
        context = "\n\n".join([
            f"[Document {i+1}] (Score: {result.scorce:.3f}):\n{result.payload.get('content', result.payload.get('context', ''))}"
            for i, result in enumerate(results)
        ])
        
        print("Context built successfully")
        
        state["context"] = context
        
        # Generate answer
        rag_prompt = f"""You are a helpful RAG assistant. Answer the question based on the provided context.

Context:
{context}

Question: {question}

Provide a clear and concise answer in Vietnamese."""
        
        messages = [SystemMessage(content=rag_prompt)]
        response = llm.invoke(messages)
        
        print("Answer generated successfully")
        
        state["answer"] = response.content
        state["messages"].append(AIMessage(content=response.content))
        
    except Exception as e:
        import traceback
        error_msg = f"RAG error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        state["error"] = error_msg
        state["answer"] = "Xin lỗi, tôi không thể truy xuất thông tin từ cơ sở tri thức."
    
    return state


def database_agent(state: AgentState) -> AgentState:
    """Database agent - handles MySQL operations via MCP"""
    question = state["question"]
    messages = state["messages"]
    
    try:
        # System prompt for database agent
        db_system_prompt = """You are a dormitory management assistant. Use the available tools to:
        - List available rooms
        - Add students to rooms
        - Get student information
        - Get room information
        - Remove students

        Always call the appropriate tool based on the user's request. Respond in Vietnamese."""
        
        messages_with_system = [SystemMessage(content=db_system_prompt)] + messages
        
        # Invoke LLM with tools
        response = llm_with_db_tools.invoke(messages_with_system)
        
        # Check if tool calls are needed
        if response.tool_calls:
            # Execute tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Find and execute tool
                tool_map = {t.name: t for t in database_tools}
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                    tool_results.append(result)
            
            # Generate final response based on tool results
            result_text = json.dumps(tool_results, ensure_ascii=False, indent=2)
            
            final_prompt = f"""Based on the tool execution results, provide a clear answer in Vietnamese.

Tool Results:
{result_text}

User Question: {question}

Provide a natural, conversational response."""
            
            final_response = llm.invoke([SystemMessage(content=final_prompt)])
            state["answer"] = final_response.content
        else:
            state["answer"] = response.content
        
        state["messages"].append(AIMessage(content=state["answer"]))
        
    except Exception as e:
        state["error"] = f"Database error: {str(e)}"
        state["answer"] = "Xin lỗi, có lỗi khi truy cập cơ sở dữ liệu. Vui lòng kiểm tra kết nối MySQL."
    
    return state


def web_search_agent(state: AgentState) -> AgentState:
    """Web search agent - searches the web for current information"""
    question = state["question"]
    messages = state["messages"]
    
    try:
        # System prompt for web search agent
        search_system_prompt = """You are a web search assistant. Use the web_search tool to find current information.
                                After getting search results, synthesize them into a clear answer in Vietnamese."""
        
        messages_with_system = [SystemMessage(content=search_system_prompt)] + messages
        
        # Invoke LLM with web search tool
        response = llm_with_web_tools.invoke(messages_with_system)
        
        # Check if tool calls are needed
        if response.tool_calls:
            # Execute web search
            search_results = []
            for tool_call in response.tool_calls:
                if tool_call["name"] == "web_search":
                    query = tool_call["args"].get("query", question)
                    result = web_search.invoke({"query": query})
                    search_results.append(result)
            
            # Generate answer from search results
            results_text = "\n\n".join(search_results)
            
            final_prompt = f"""Based on the web search results, answer the question in Vietnamese.

                                Search Results:
                                {results_text}

                                Question: {question}

                                Provide a clear, informative answer."""
            
            final_response = llm.invoke([SystemMessage(content=final_prompt)])
            state["answer"] = final_response.content
        else:
            state["answer"] = response.content
        
        state["messages"].append(AIMessage(content=state["answer"]))
        
    except Exception as e:
        state["error"] = f"Web search error: {str(e)}"
        state["answer"] = "Xin lỗi, không thể tìm kiếm thông tin trên web."
    
    return state


def route_to_agent(state: AgentState) -> Literal["rag_agent", "database_agent", "web_search_agent"]:
    """Route to appropriate agent based on classification"""
    route = state.get("route", "rag")
    
    if route == "database":
        return "database_agent"
    elif route == "web_search":
        return "web_search_agent"
    else:
        return "rag_agent"


# ============================================================================
# Build Graph
# ============================================================================

def build_graph():
    """Build the LangGraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("route_question", route_question)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("database_agent", database_agent)
    workflow.add_node("web_search_agent", web_search_agent)
    
    # Set entry point
    workflow.set_entry_point("route_question")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "route_question",
        route_to_agent,
        {
            "rag_agent": "rag_agent",
            "database_agent": "database_agent",
            "web_search_agent": "web_search_agent"
        }
    )
    
    # All agents end the workflow
    workflow.add_edge("rag_agent", END)
    workflow.add_edge("database_agent", END)
    workflow.add_edge("web_search_agent", END)
    
    return workflow.compile()


# Global graph instance
_graph = None

def get_graph():
    """Get or create graph instance"""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


# ============================================================================
# API Endpoints
# ============================================================================

class QuestionRequest(BaseModel):
    question: str


@app.post("/search")
async def search_endpoint(payload: QuestionRequest):
    """
    Main endpoint for agentic RAG system
    Routes questions to appropriate agent (RAG, Database, or Web Search)
    """
    question = payload.question
    
    if not question:
        return {"ok": False, "error": "Empty question"}
    
    try:
        # Get graph
        graph = get_graph()
        
        # Initialize state
        initial_state = {
            "messages": [],
            "question": question,
            "route": "",
            "context": "",
            "answer": "",
            "error": ""
        }
        
        # Run graph with async support
        result = await graph.ainvoke(initial_state)
        
        # Extract answer
        answer = result.get("answer", "No answer generated")
        route = result.get("route", "unknown")
        error = result.get("error", "")
        
        if error:
            return {
                "ok": False,
                "error": error,
                "route": route,
                "answer": answer
            }
        
        return {
            "ok": True,
            "route": route,
            "answer": answer
        }
        
    except Exception as e:
        import traceback
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
