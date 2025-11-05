import json
import requests
import streamlit as st

st.title("Chatbot RAG - Semantic Route API")

# URL mới của API
API_URL = "http://localhost:8000/rag_core/search"

# Hàm gọi API RAG mới
def call_rag_api(messages):
    payload = {
        "data": messages  # Dạng list các dict {"role": ..., "content": ...}
    }

    response = requests.post(API_URL, json=payload, timeout=60)
    if response.status_code != 200:
        raise Exception(f"API lỗi: {response.text}")
    return response.json()


# Lưu trữ lịch sử hội thoại
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn trước đó
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ô nhập prompt người dùng
if prompt := st.chat_input("Hãy đặt câu hỏi về  bất cứ điều gì..."):
    user_msg = {
        "role": "user",
        "content": prompt
    }
    st.session_state.messages.append(user_msg)

    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Gửi toàn bộ lịch sử hội thoại (bao gồm prompt mới)
            response = call_rag_api(st.session_state.messages)
            reply = response.get("content", "Không có phản hồi.")
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(str(e))
            st.session_state.messages.append({"role": "assistant", "content": "Đã xảy ra lỗi khi gọi API."})
