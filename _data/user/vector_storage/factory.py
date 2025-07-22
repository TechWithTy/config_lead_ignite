from typing import Optional, Union, Dict, Any
from .interfaces import VectorDatabase
from .services.supabase_service import SupabaseVectorService
from .services.postgres_service import PostgresVectorService

class VectorDBFactory:
    """Factory for creating vector database instances"""
    
    @staticmethod
    def create_vector_db(
        db_type: str = "supabase",
        **kwargs
    ) -> VectorDatabase:
        """
        Create a vector database instance
        
        Args:
            db_type: Either 'supabase' or 'postgres'
            **kwargs: Database connection parameters
                For Supabase: supabase_url, supabase_key
                For PostgreSQL: database_url
                
        Returns:
            An instance of VectorDatabase
            
        Raises:
            ValueError: If db_type is invalid or required parameters are missing
        """
        if db_type == "supabase":
            required = ['supabase_url', 'supabase_key']
            missing = [param for param in required if param not in kwargs]
            if missing:
                raise ValueError(f"Missing required parameters for Supabase: {', '.join(missing)}")
            return SupabaseVectorService(
                supabase_url=kwargs['supabase_url'],
                supabase_key=kwargs['supabase_key']
            )
            
        elif db_type == "postgres":
            if 'database_url' not in kwargs:
                raise ValueError("Missing required parameter for PostgreSQL: database_url")
            return PostgresVectorService(database_url=kwargs['database_url'])
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> VectorDatabase:
        """
        Create a vector database instance from a configuration dictionary
        
        Example config:
            {
                "type": "supabase",
                "supabase_url": "https://your-project.supabase.co",
                "supabase_key": "your-anon-key"
            }
            
        or:
            {
                "type": "postgres",
                "database_url": "postgresql+asyncpg://user:pass@localhost:5432/vectordb"
            }
        """
        db_type = config.get('type', 'supabase')
        return cls.create_vector_db(db_type=db_type, **config)
