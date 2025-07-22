from typing import Optional, List, Dict, Any
import json
from supabase import create_client, Client
from ..models.collection import VectorCollection
from ..models.embedding import VectorEmbedding
from ..interfaces import VectorDatabase

class SupabaseVectorService(VectorDatabase):
    """Service for handling vector operations with Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    async def create_collection(self, collection: VectorCollection) -> Dict[str, Any]:
        """Create a new vector collection"""
        result = self.supabase.table('vector_collections').insert(collection.dict()).execute()
        return result.data[0] if result.data else None
    
    async def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector collection by ID"""
        result = self.supabase.table('vector_collections').select('*').eq('id', collection_id).execute()
        return result.data[0] if result.data else None
    
    async def add_embeddings(
        self, 
        collection_id: str,
        embeddings: List[VectorEmbedding]
    ) -> List[Dict[str, Any]]:
        """Add multiple embeddings to a collection"""
        if not embeddings:
            return []
            
        data = [{
            **e.dict(exclude={'id', 'created_at', 'updated_at'}),
            'collection_id': collection_id
        } for e in embeddings]
        
        result = self.supabase.table('vector_embeddings').insert(data).execute()
        return result.data if result.data else []
    
    async def search_similar(
        self,
        collection_id: str,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in a collection"""
        # Use Supabase's RPC for vector search
        result = self.supabase.rpc(
            'match_embeddings',
            {
                'query_embedding': query_embedding,
                'match_count': limit,
                'filter': {'collection_id': collection_id}
            }
        ).execute()
        
        # Filter by minimum similarity
        return [
            item for item in result.data 
            if item.get('similarity', 0) >= min_similarity
        ]
    
    async def create_index(
        self, 
        collection_id: str, 
        index_type: str = "ivfflat",
        index_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a vector index for a collection"""
        if index_params is None:
            index_params = {}
            
        # Default parameters for IVFFlat
        if index_type.lower() == "ivfflat":
            index_params = {
                'lists': index_params.get('lists', 100),
                'metric': index_params.get('metric', 'cosine')
            }
        
        try:
            # Update collection with index info
            await self.update_collection(
                collection_id, 
                index_type=index_type,
                index_params=index_params
            )
            
            # Create the actual index in Supabase
            index_name = f"idx_embeddings_{collection_id.replace('-', '_')}"
            column_name = 'embedding'  # Assuming this is the column name in your table
            
            # This would be a raw SQL execution - adjust based on your Supabase setup
            self.supabase.rpc('create_vector_index', {
                'index_name': index_name,
                'table_name': 'vector_embeddings',
                'column_name': column_name,
                'index_type': index_type,
                'parameters': json.dumps(index_params)
            }).execute()
            
            return True
            
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            return False
    
    async def update_collection(
        self, 
        collection_id: str, 
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update a collection's properties"""
        if not updates:
            return None
            
        result = self.supabase.table('vector_collections').update(updates).eq('id', collection_id).execute()
        return result.data[0] if result.data else None
