from typing import List, Optional, Dict, Any
from pydantic import Field
import numpy as np
from .base import VectorBaseModel

class VectorEmbedding(VectorBaseModel):
    """Model for storing vector embeddings with metadata"""
    collection_id: str  # Reference to VectorCollection
    vector: List[float]  # The actual embedding vector
    text: Optional[str] = None  # Original text if applicable
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata
    
    def to_numpy(self) -> np.ndarray:
        """Convert vector to numpy array"""
        return np.array(self.vector, dtype=np.float32)
    
    @classmethod
    def from_numpy(cls, vector: np.ndarray, **kwargs) -> 'VectorEmbedding':
        """Create from numpy array"""
        return cls(vector=vector.tolist(), **kwargs)
