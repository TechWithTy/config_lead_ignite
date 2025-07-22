"""
Vector Storage Module

This module provides vector storage functionality with support for both PostgreSQL and Supabase.
It includes models, services, and adapters for managing vector embeddings and collections.
"""

from .models.collection import VectorCollection
from .models.embedding import VectorEmbedding
from .services.vector_service import VectorService, VectorCollectionService, VectorEmbeddingService
from .services.supabase_service import SupabaseVectorService
from .services.postgres_service import PostgresVectorService
from .factory import VectorDBFactory
from .interfaces import VectorDatabase

__all__ = [
    # Models
    'VectorCollection',
    'VectorEmbedding',
    
    # Services
    'VectorService',
    'VectorCollectionService',
    'VectorEmbeddingService',
    
    # Database Implementations
    'SupabaseVectorService',
    'PostgresVectorService',
    
    # Factory
    'VectorDBFactory',
    
    # Interfaces
    'VectorDatabase'
]
