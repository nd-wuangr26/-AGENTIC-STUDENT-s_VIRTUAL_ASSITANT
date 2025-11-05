import google.generativeai as genai
from app.core.config.config import *

class GeminiLLM:
    def __init__(self, model_name = MODEL_NAME_LLM, api_key: str = None):
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(model_name=model_name)
        self.template = None
    
    def generate_content(self, query: str):
        response = self.llm.generate_content(query)
        return response.text
    
    def generate_query_variant(self, query: str, n_variants: int = 5) -> list:
        prompt = f"""Tôi cần {n_variants} cách diễn đạt khác nhau cho câu hỏi sau, giữ nguyên nghĩa nhưng thay đổi cách diễn đạt hoặc cấu trúc câu.

        Câu hỏi gốc: "{query}"

        Trả về kết quả dưới dạng danh sách dòng, không giải thích gì thêm.
        """
        response = self.generate_content(prompt)
        
        # Xu ly query sau khi generative 
        response = [line.strip("-").strip() for line in response.strip().strip("/n") if line.strip()]

        return response[:n_variants]
    