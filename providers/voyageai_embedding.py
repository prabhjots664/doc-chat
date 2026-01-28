"""
Voyage AI embedding provider implementation.
"""

import requests
from typing import List, Dict, Any, Union
from interfaces.embedding_provider import IEmbeddingProvider
from domain.entities import EmbeddingResult
from core.exceptions import ProviderError, APIError
from core.logging import get_logger

logger = get_logger(__name__)


class VoyageAIEmbeddingProvider(IEmbeddingProvider):
    """Voyage AI embedding provider implementation."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "voyage-context-3",
        base_url: str = "https://api.voyageai.com/v1",
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        """
        Initialize Voyage AI embedding provider.
        
        Args:
            api_key: Voyage AI API key
            model: Model identifier (e.g., "voyage-context-3", "voyage-2")
            base_url: Voyage AI API base URL
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Model dimensions mapping
        self.dimension_map = {
            "voyage-context-3": 1024,
            "voyage-4": 1024,
            "voyage-2": 1024,
            "voyage-code-2": 1536,
            "voyage-large-2": 1536,
            "voyage-law-2": 1024
        }
        self.dimension = self.dimension_map.get(model, 1024)
        
        logger.info(f"Initialized Voyage AI provider with model: {model} (dimension={self.dimension})")
    
    def embed(
        self,
        texts: Union[List[str], List[List[str]]],
        input_type: str = "document"
    ) -> EmbeddingResult:
        """
        Generate embeddings for a list of texts.
        If using voyage-context-3, expects a list of lists of chunks for "document" input_type.
        """
        try:
            if not texts:
                raise ValueError("No texts provided for embedding")
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Determine endpoint and format
            if self.model == "voyage-context-3":
                endpoint = f"{self.base_url}/contextualizedembeddings"
                # For contextualized embeddings, input must be list of lists
                # If a flat list is provided, wrap it as a single "document"
                if isinstance(texts, list) and len(texts) > 0 and isinstance(texts[0], str):
                    formatted_inputs = [texts]
                else:
                    formatted_inputs = texts
            else:
                endpoint = f"{self.base_url}/embeddings"
                formatted_inputs = texts
                
            payload = {
                "model": self.model,
                "input": formatted_inputs if self.model != "voyage-context-3" else None,
                "inputs": formatted_inputs if self.model == "voyage-context-3" else None,
                "input_type": input_type  # "document" or "query"
            }
            # Clean up payload
            payload = {k: v for k, v in payload.items() if v is not None}
            
            logger.debug(f"Sending embedding request to Voyage AI: model={self.model}, endpoint={endpoint}")
            
            # Make request
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Handle errors
            if response.status_code != 200:
                error_msg = f"Voyage AI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise APIError(
                    error_msg,
                    status_code=response.status_code,
                    provider="VoyageAI"
                )
            
            # Parse response
            data = response.json()
            
            if "error" in data:
                error_msg = f"Voyage AI returned error: {data['error']}"
                logger.error(error_msg)
                raise APIError(error_msg, provider="VoyageAI")
            
            # Extract embeddings based on model type
            embeddings = []
            if self.model == "voyage-context-3":
                # contextualizedembeddings returns results within 'data' but nested differently
                # { "data": [ { "data": [ {"embedding": [...]}, ... ] }, ... ] }
                for doc_result in data["data"]:
                    for chunk_result in doc_result["data"]:
                        embeddings.append(chunk_result["embedding"])
            else:
                # standard embeddings: { "data": [ {"embedding": [...]}, ... ] }
                embeddings = [item["embedding"] for item in data["data"]]
                
            usage = data.get("usage", {})
            
            result = EmbeddingResult(
                embeddings=embeddings,
                model=data.get("model", self.model),
                dimension=len(embeddings[0]) if embeddings else self.dimension,
                tokens_used=usage.get("total_tokens", 0),
                metadata={
                    "input_type": input_type,
                    "num_elements": len(embeddings)
                }
            )
            
            logger.info(f"Generated {len(embeddings)} embeddings: {result.tokens_used} tokens")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Voyage AI request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ProviderError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Voyage AI request failed: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in Voyage AI provider: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.dimension
    
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return f"VoyageAI ({self.model})"
    
    def validate_connection(self) -> bool:
        """Validate that the provider is accessible."""
        try:
            # Simple test embedding
            test_result = self.embed(
                texts=["test"],
                input_type="document"
            )
            
            logger.info("Voyage AI connection validated successfully")
            return True
            
        except Exception as e:
            error_msg = f"Voyage AI connection validation failed: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
