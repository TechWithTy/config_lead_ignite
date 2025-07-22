from typing import Optional, List
from pydantic import Field
from .base import VectorBaseModel

class VectorCollection(VectorBaseModel):
    """Model for organizing vector embeddings into collections"""
    name: str  # Unique name for the collection
    description: Optional[str] = None
    dimensions: int  # Dimensionality of vectors in this collection
    metadata: dict = Field(default_factory=dict)  # Collection-level metadata
    is_public: bool = False
    
    # Index configuration
    index_type: str = "ivfflat"  # Default index type
    index_params: dict = Field(default_factory=dict)  # Index-specific parameters
    
    class Config:
        schema_extra = {
            "example": {
                "name": "blog_embeddings",
                "description": "Embeddings for blog posts",
                "dimensions": 1536,
                "is_public": False,
                "index_type": "ivfflat",
                "index_params": {"lists": 100, "metric": "cosine"}
            }
        }
