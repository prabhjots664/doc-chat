"""
Custom exceptions for the doc-chat system.
"""


class DocChatException(Exception):
    """Base exception for all doc-chat errors."""
    pass


class ConfigurationError(DocChatException):
    """Configuration-related errors."""
    pass


class ProviderError(DocChatException):
    """Provider-related errors (LLM, Embedding, VectorStore)."""
    pass


class DocumentProcessingError(DocChatException):
    """Document processing errors."""
    pass


class ValidationError(DocChatException):
    """Input validation errors."""
    pass


class APIError(ProviderError):
    """External API errors."""
    
    def __init__(self, message: str, status_code: int = None, provider: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.provider = provider
