from typing import Optional, List, Dict, Any, cast
import json
from sqlalchemy import create_engine, text, select, update, delete, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from ..models.collection import VectorCollection
from ..models.embedding import VectorEmbedding
from ..interfaces import VectorDatabase

class PostgresVectorService(VectorDatabase):
    """Service for handling vector operations with PostgreSQL"""
    
    def __init__(self, database_url: str):
        """
        Initialize the PostgreSQL vector service
        
        Args:
            database_url: PostgreSQL connection URL (e.g., 'postgresql+asyncpg://user:pass@localhost/db')
        """
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def create_collection(self, collection: VectorCollection) -> Dict[str, Any]:
        """Create a new vector collection"""
        async with self.async_session() as session:
            query = """
            INSERT INTO vector_collections (
                id, name, description, dimensions, metadata, 
                is_public, index_type, index_params, created_at, updated_at
            ) VALUES (
                :id, :name, :description, :dimensions, :metadata::jsonb,
                :is_public, :index_type, :index_params::jsonb, :created_at, :updated_at
            )
            RETURNING *
            """
            
            result = await session.execute(
                text(query),
                {
                    **collection.dict(),
                    'metadata': json.dumps(collection.metadata or {}),
                    'index_params': json.dumps(collection.index_params or {})
                }
            )
            await session.commit()
            return dict(result.first())
    
    async def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector collection by ID"""
        async with self.async_session() as session:
            result = await session.execute(
                text("SELECT * FROM vector_collections WHERE id = :id"),
                {'id': collection_id}
            )
            row = result.first()
            return dict(row) if row else None
    
    async def add_embeddings(
        self, 
        collection_id: str,
        embeddings: List[VectorEmbedding]
    ) -> List[Dict[str, Any]]:
        """Add multiple embeddings to a collection"""
        if not embeddings:
            return []
            
        async with self.async_session() as session:
            query = """
            INSERT INTO vector_embeddings (
                id, collection_id, vector, text, metadata, created_at, updated_at
            ) VALUES (
                :id, :collection_id, :vector::vector, :text, :metadata::jsonb, 
                :created_at, :updated_at
            )
            RETURNING *
            """
            
            results = []
            for emb in embeddings:
                result = await session.execute(
                    text(query),
                    {
                        **emb.dict(),
                        'collection_id': collection_id,
                        'metadata': json.dumps(emb.metadata or {})
                    }
                )
                results.append(dict(result.first()))
            
            await session.commit()
            return results
    
    async def search_similar(
        self,
        collection_id: str,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors in a collection using cosine similarity"""
        async with self.async_session() as session:
            query = """
            SELECT 
                id, collection_id, vector, text, metadata, 
                created_at, updated_at,
                1 - (vector <=> :query_embedding::vector) as similarity
            FROM vector_embeddings
            WHERE collection_id = :collection_id
            AND 1 - (vector <=> :query_embedding::vector) >= :min_similarity
            ORDER BY vector <=> :query_embedding::vector
            LIMIT :limit
            """
            
            result = await session.execute(
                text(query),
                {
                    'collection_id': collection_id,
                    'query_embedding': query_embedding,
                    'min_similarity': min_similarity,
                    'limit': limit
                }
            )
            
            return [dict(row) for row in result]
    
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
            lists = index_params.get('lists', 100)
            metric = index_params.get('metric', 'cosine')
            
            # Get vector dimension from collection
            collection = await self.get_collection(collection_id)
            if not collection:
                return False
                
            dimension = collection['dimensions']
            
            index_name = f"idx_embeddings_{collection_id.replace('-', '_')}"
            
            try:
                async with self.async_session() as session:
                    # Create the index
                    create_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON vector_embeddings USING {index_type} (vector {metric}_ops)
                    WITH (lists = {lists})
                    WHERE collection_id = '{collection_id}'
                    """
                    
                    await session.execute(text(create_index_sql))
                    await session.commit()
                    
                    # Update collection with index info
                    await self.update_collection(
                        collection_id,
                        index_type=index_type,
                        index_params=index_params
                    )
                    
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
            
        async with self.async_session() as session:
            # Convert metadata and index_params to JSON if they exist
            if 'metadata' in updates and updates['metadata'] is not None:
                updates['metadata'] = json.dumps(updates['metadata'])
            if 'index_params' in updates and updates['index_params'] is not None:
                updates['index_params'] = json.dumps(updates['index_params'])
            
            # Add updated_at timestamp
            updates['updated_at'] = 'NOW()'
            
            set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
            
            query = f"""
            UPDATE vector_collections
            SET {set_clause}
            WHERE id = :collection_id
            RETURNING *
            """
            
            result = await session.execute(
                text(query),
                {'collection_id': collection_id, **updates}
            )
            
            await session.commit()
            row = result.first()
            return dict(row) if row else None
