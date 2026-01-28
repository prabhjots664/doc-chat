"""
OpenRouter LLM provider implementation.
Supports multiple models through OpenRouter's unified API.
"""

import requests
from typing import List, Dict, Any, Optional
from interfaces.llm_provider import ILLMProvider
from domain.entities import LLMMessage, LLMResponse
from core.exceptions import ProviderError, APIError
from core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterLLMProvider(ILLMProvider):
    """OpenRouter LLM provider implementation."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "z-ai/glm-4.5-air:free",
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        """
        Initialize OpenRouter LLM provider.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier (e.g., "z-ai/glm-4.5-air:free")
            base_url: OpenRouter API base URL
            site_url: Optional site URL for rankings
            site_name: Optional site name for rankings
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.site_url = site_url
        self.site_name = site_name
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        logger.info(f"Initialized OpenRouter provider with model: {model}")
    
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        try:
            # Convert messages to OpenAI format
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add optional headers
            if self.site_url:
                headers["HTTP-Referer"] = self.site_url
            if self.site_name:
                headers["X-Title"] = self.site_name
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            logger.debug(f"Sending request to OpenRouter: model={self.model}, messages={len(messages)}")
            
            # Make request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            # Handle errors
            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise APIError(
                    error_msg,
                    status_code=response.status_code,
                    provider="OpenRouter"
                )
            
            # Parse response
            data = response.json()
            
            if "error" in data:
                error_msg = f"OpenRouter returned error: {data['error']}"
                logger.error(error_msg)
                raise APIError(error_msg, provider="OpenRouter")
            
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            result = LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", self.model),
                tokens_used=usage.get("total_tokens", 0),
                finish_reason=choice.get("finish_reason", "unknown"),
                metadata={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "id": data.get("id", "")
                }
            )
            
            logger.info(f"Generated response: {result.tokens_used} tokens, finish_reason={result.finish_reason}")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"OpenRouter request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise ProviderError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenRouter request failed: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in OpenRouter provider: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
    
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        return f"OpenRouter ({self.model})"
    
    def validate_connection(self) -> bool:
        """Validate that the provider is accessible."""
        try:
            # Simple test message
            test_messages = [
                LLMMessage(role="user", content="Hello")
            ]
            
            response = self.generate(
                messages=test_messages,
                max_tokens=10,
                temperature=0.0
            )
            
            logger.info("OpenRouter connection validated successfully")
            return True
            
        except Exception as e:
            error_msg = f"OpenRouter connection validation failed: {str(e)}"
            logger.error(error_msg)
            raise ProviderError(error_msg)
