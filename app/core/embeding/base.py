from pydantic.v1 import BaseModel, Field, validator
from typing import Any

class EmbeddingConfig(BaseModel):
    model_name: str = Field(
        ...,
        description="The name of the embedding model to use."
    )

    @validator('model_name')
    def validate_model_name(cls, v):
        if not v:
            raise ValueError("Model name cannot be empty.")
        return v

class BaseEmbedding():
    name : str

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def encode(self, text: str) -> Any:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
class APIBaseEmbedding(BaseEmbedding):

    base_url: str
    apikey: str

    def __init__(self, name: str, base_url: str = None, apikey: str = None):
        super().__init__(name)
        self.base_url = base_url
        self.apikey = apikey