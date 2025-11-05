from sentence_transformers import CrossEncoder
from app.core.config.config import *
import numpy as np

class ReRank():
    def __init__(self, model_name : str = MODEL_RERANK):
        self.re_rank = CrossEncoder(model_name, device="cpu")
        
    def __call__(self, query : str, passages : list[str]) -> tuple[list[float], list[str]]:
        # Gop query voi chunks 
        query_passages_pairs = ([query, passage] for passage in passages)
        
        # Lay diem cua doan van
        scores = self.re_rank.predict(list(query_passages_pairs))
        
        # Sort doan van theo diem
        rank_passages = [passage for _, passage in sorted(zip(scores, passages), key=lambda x : x[0], reverse=True)] 
        rank_scores = sorted(scores, reverse=True)
        
        return rank_scores, rank_passages