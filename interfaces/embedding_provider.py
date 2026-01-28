"""Interface for embedding providers."""

from abc import ABC, abstractmethod
from typing import List
from domain.entities import EmbeddingResult


class IEmbeddingProvider(ABC):
    """Abstract interface for embedding providers (Voyage AI, etc.)."""
    
    @abstractmethod
    def embed(
        self,
        texts: List[str],
        input_type: str = "document"
    ) -> EmbeddingResult:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            input_type: Type of input ("document" or "query")
            
        Returns:
            EmbeddingResult with embeddings and metadata
            
        Raises:
            ProviderError: If embedding generation fails
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the provider is accessible.
        
        Returns:
            True if connection is valid
            
        Raises:
            ProviderError: If connection fails
        """
        pass
