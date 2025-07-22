from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from pydantic import BaseModel
from ...core import get_supabase_client
from ..models.collection import VectorCollection
from ..models.embedding import VectorEmbedding


T = TypeVar('T', bound=BaseModel)

class VectorService(Generic[T]):
    """Base service for vector operations with Supabase"""
    
    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class
        self.supabase = get_supabase_client()
    
    async def create(self, data: T) -> T:
        """Create a new vector record"""
        result = self.supabase.table(self.table_name).insert(data.model_dump()).execute()
        return self.model_class(**result.data[0])
    
    async def get(self, id: str) -> Optional[T]:
        """Get a vector record by ID"""
        result = self.supabase.table(self.table_name).select('*').eq('id', id).execute()
        return self.model_class(**result.data[0]) if result.data else None
    
    async def update(self, id: str, data: T) -> T:
        """Update a vector record"""
        result = self.supabase.table(self.table_name).update(data.dict()).eq('id', id).execute()
        return self.model_class(**result.data[0])
    
    async def delete(self, id: str) -> bool:
        """Soft delete a vector record"""
        result = self.supabase.table(self.table_name).update({'is_deleted': True}).eq('id', id).execute()
        return len(result.data) > 0
    
    async def vector_search(
        self,
        query_embedding: List[float],
        collection_id: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using Supabase's vector search"""
        result = self.supabase.rpc(
            'match_vectors',
            {
                'query_embedding': query_embedding,
                'match_count': limit,
                'filter': {'collection_id': collection_id}
            }
        ).execute()
        
        # Filter by threshold and map to model instances
        matches = [
            self.model_class(**item) 
            for item in result.data 
            if item.get('similarity', 0) >= threshold
        ]
        
        return matches


class VectorCollectionService(VectorService[VectorCollection]):
    """Service for managing vector collections"""
    def __init__(self):
        super().__init__('vector_collections', VectorCollection)
    
    async def get_by_name(self, name: str) -> Optional[VectorCollection]:
        """Get a collection by name"""
        result = self.supabase.table(self.table_name).select('*').eq('name', name).execute()
        return self.model_class(**result.data[0]) if result.data else None


class VectorEmbeddingService(VectorService[VectorEmbedding]):
    """Service for managing vector embeddings"""
    def __init__(self):
        super().__init__('vector_embeddings', VectorEmbedding)
    
    async def batch_create(self, embeddings: List[VectorEmbedding]) -> List[VectorEmbedding]:
        """Create multiple embeddings in a single batch"""
        if not embeddings:
            return []
            
        data = [e.dict() for e in embeddings]
        result = self.supabase.table(self.table_name).insert(data).execute()
        return [self.model_class(**item) for item in result.data]
