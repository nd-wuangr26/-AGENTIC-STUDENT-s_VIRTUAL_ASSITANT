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
    