"""Interface for vector store providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from domain.entities import SearchResult


class IVectorStore(ABC):
    """Abstract interface for vector store providers (Qdrant, etc.)."""
    
    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "cosine"
    ) -> bool:
        """
        Create a new collection.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors
            distance_metric: Distance metric to use
            
        Returns:
            True if successful
            
        Raises:
            ProviderError: If creation fails
        """
        pass
    
    @abstractmethod
    def upsert(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Insert or update vectors in the collection.
        
        Args:
            collection_name: Name of the collection
            vectors: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of IDs (generated if not provided)
            
        Returns:
            True if successful
            
        Raises:
            ProviderError: If upsert fails
        """
        pass
    
    @abstractmethod
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query embedding vector
            limit: Number of results to return
            filter_conditions: Optional metadata filters
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ProviderError: If search fails
        """
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection information
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the vector store is accessible.
        
        Returns:
            True if connection is valid
            
        Raises:
            ProviderError: If connection fails
        """
        pass
