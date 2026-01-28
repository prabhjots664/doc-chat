"""Interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.entities import LLMMessage, LLMResponse


class ILLMProvider(ABC):
    """Abstract interface for LLM providers (OpenRouter, etc.)."""
    
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            ProviderError: If generation fails
        """
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
