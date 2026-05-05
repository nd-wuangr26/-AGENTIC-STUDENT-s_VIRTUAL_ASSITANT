# 🎓 Agentic RAG System for Dormitory Management

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.1-orange.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)

Hệ thống **Agentic RAG** thông minh dành cho quản lý ký túc xá, tích hợp kiến trúc Multi-Agent với LangGraph, cơ sở dữ liệu Vector Qdrant và MySQL. Hệ thống cung cấp khả năng trả lời câu hỏi tự động, quản lý sinh viên/phòng ở, và tìm kiếm thông tin thời gian thực.

---

## 🚀 Tính Năng Nổi Bật (Key Features)

### 🧠 1. Kiến Trúc Multi-Agent (AI Core)
Hệ thống sử dụng **LangGraph** để điều phối các agent chuyên biệt:
- **Router Agent**: Phân tích ý định người dùng (Intent Classification) để định tuyến câu hỏi đến agent phù hợp.
- **RAG Agent**: Truy vấn tài liệu quy chế, hướng dẫn từ **Qdrant Vector DB** để trả lời các câu hỏi chung.
- **Database Agent**: Tương tác trực tiếp với **MySQL** để tra cứu thông tin phòng, sinh viên, điện nước (sử dụng MCP - Model Context Protocol).
- **Web Search Agent**: Tìm kiếm thông tin thời gian thực (tin tức, thời tiết) qua **Google Search (Serper API)**.

### 🔐 2. Xác Thực & Phân Quyền (Authentication)
- **JWT Authentication**: Bảo mật đăng nhập và phiên làm việc.
- **User Roles**:
  - **Student (User)**: Đăng ký bằng MSSV, chat với bot, xem lịch sử chat.
  - **Admin**: Quyền quản trị cao cấp, truy cập Dashboard.

### 📊 3. Admin Dashboard
Giao diện quản trị dành riêng cho Admin:
- **Thống kê tổng quan**: Số lượng tòa nhà, phòng, sinh viên, tỉ lệ lấp đầy.
- **Quản lý phòng**: Xem trạng thái từng phòng (trống/đầy), số lượng sinh viên hiện tại.
- **Thống kê theo tòa**: Chi tiết cho các tòa A, B, C, D.
- **Quản lý sinh viên**: Danh sách toàn bộ sinh viên.
- **Document Management**: **Upload tài liệu** trực tiếp để hệ thống tự động chunking và vector hóa vào Qdrant.

### 💬 4. Chat History & Session Management
- **Lưu trữ lịch sử**: Tự động lưu toàn bộ hội thoại vào MySQL.
- **Quản lý phiên chat**: Tạo mới, đổi tên, xóa phiên chat.
- **Context Awareness**: Bot ghi nhớ ngữ cảnh trong phiên làm việc.

---

## 🏗️ Kiến Trúc Hệ Thống (Architecture)

```
┌─────────────────────────────────────────────┐
│           User Question                      │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│     Router Agent (LLM Classification)        │
│  - Phân tích intent của câu hỏi             │
│  - Route đến agent phù hợp                  │
└──────────┬──────────┬──────────┬────────────┘
           │          │          │
    ┌──────┴───┐  ┌──┴────┐  ┌──┴─────────┐
    │   RAG    │  │  DB   │  │ Web Search │
    │  Agent   │  │ Agent │  │   Agent    │
    └────┬─────┘  └───┬───┘  └─────┬──────┘
         │            │             │
    ┌────┴─────┐ ┌───┴────┐   ┌────┴─────┐
    │ Qdrant   │ │ MySQL  │   │  Serper  │
    │ Vector   │ │  MCP   │   │  Google  │
    │   DB     │ │ Server │   │  Search  │
    └──────────┘ └────────┘   └──────────┘
```

## 🛠️ Yêu Cầu Hệ Thống (Prerequisites)

- **Python**: 3.11 trở lên
- **MySQL Server**: 8.0+
- **Docker**: Để chạy Qdrant (khuyến nghị)
- **API Keys**:
  - OpenAI API Key (cho LLM & Embeddings)
  - Serper API Key (cho Web Search)

---

## ⚙️ Cài Đặt & Thiết Lập (Installation)

### 1. Clone Repository
```bash
git clone <repository-url>
cd RAG_QrandtDB
```

### 2. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu Hình Môi Trường (.env)
Tạo file `.env` từ `.env.example` và điền thông tin:
```bash
cp .env.example .env
```
Nội dung file `.env` cần có:
```env
# Database Config
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=dormitory_db

# Qdrant Config
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key (nếu có)

# API Keys
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...

# JWT Config
SECRET_KEY=your_secret_key_hash
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Khởi Chạy Database
**Qdrant (Vector DB):**
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

**MySQL (Relational DB):**
Tạo database và bảng từ file SQL:
```bash
mysql -u root -p < init_database.sql
```

### 5. Tạo Tài Khoản Admin
Chạy script để tạo tài khoản admin đầu tiên:
```bash
python create_admin.py
# Nhập username và password khi được hỏi
```

---

## 🚀 Hướng Dẫn Sử Dụng (Usage)

### 1. Khởi Chạy Backend Server
```bash
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```
Server sẽ chạy tại: `http://127.0.0.1:8000`
Swagger UI (API Docs): `http://127.0.0.1:8000/docs`

### 2. Khởi Chạy Frontend
Mở file `font-end/v2/index.html` trực tiếp trên trình duyệt hoặc sử dụng Live Server của VS Code.

---

## 📚 API Documentation

### 🔐 Authentication (`/api/auth`)
- `POST /login`: Đăng nhập (trả về JWT Token).
- `POST /register`: Đăng ký tài khoản sinh viên (Username = MSSV).
- `GET /me`: Lấy thông tin user hiện tại.

### 🤖 RAG Generation (`/api/generate`)
- `POST /search`: Gửi câu hỏi cho hệ thống Agentic RAG xử lý.

### 💬 Chat History (`/api/chat`)
- `GET /sessions`: Lấy danh sách phiên chat.
- `POST /sessions`: Tạo phiên chat mới.
- `GET /sessions/{id}`: Lấy nội dung tin nhắn của phiên.
- `POST /messages`: Lưu tin nhắn mới.

### 🛡️ Admin Dashboard (`/api/admin`)
- `GET /overview`: Thống kê toàn bộ hệ thống.
- `GET /buildings/{id}`: Thống kê chi tiết tòa nhà.
- `GET /rooms`: Trạng thái phòng ở.
- `POST /upload`: **Upload tài liệu** (PDF/Doc) để training cho bot.

---

## 📂 Cấu Trúc Dự Án (Project Structure)

```
RAG_QrandtDB/
├── app/
│   ├── api/                 # API Routes (Auth, Admin, Chat, RAG)
│   ├── core/                # Core Logic (Config, Schema, Services)
│   ├── rag/                 # RAG Logic (LangGraph Agents)
│   └── startup/             # Startup Events (DB Init)
├── document/                # Thư mục chứa tài liệu upload
├── font-end/                # Frontend Source Code
│   └── v2/                  # Version 2 UI (Recommended)
├── create_admin.py          # Script tạo admin
├── init_database.sql        # Script khởi tạo MySQL
├── server.py                # Main Entry Point
├── requirements.txt         # Python Dependencies
└── README.md                # Documentation
```

---


## 🙏 Acknowledgments

- LangGraph by LangChain
- OpenAI for embeddings and LLM
- Qdrant for vector database
- Serper for Google Search API
