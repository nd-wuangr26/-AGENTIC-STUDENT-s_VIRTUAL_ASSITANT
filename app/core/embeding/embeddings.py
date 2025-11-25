from pathlib import Path
import sys

# Lên 3 cấp từ file hiện tại để đến thư mục chứa "app"
project_root = Path(__file__).resolve().parents[2]

# Thêm vào sys.path nếu chưa có
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
from .base import BaseEmbedding
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from app.core.config.config import *

class Embedding(BaseEmbedding):
    def __init__(self, name):
        super().__init__(name= name)
        self.name_model = HuggingFaceEmbeddings(model_name=name)
        
    
    def encode(self, text:List[str]):
        vector = self.name_model.embed_documents(text)
        return vector[0] if len(vector)==1 else vector
    
# Thêm phương thức __call__ và đảm bảo nó là async
    async def __call__(self, text: str | list[str]) -> list:
        """Thực hiện logic tạo vector nhúng."""
        # Ví dụ: Gọi hàm tạo nhúng thực sự của bạn
        if isinstance(text, str):
            return self.encode(text) # Giả sử self.encode() là hàm tạo nhúng