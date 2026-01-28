"""
Factory class for building the ChatService and its dependencies.
"""

from core.config import Config
from services.chat_service import ChatService
from core.logging import setup_logging


class ServiceFactory:
    """Factory for centralized service creation."""
    
    @staticmethod
    def create_chat_service(config_path: str = None) -> ChatService:
        """
        Create and initialize the ChatService.
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Initialized ChatService
        """
        # 1. Initialize configuration
        config = Config(config_path)
        
        # 2. Setup logging based on config
        setup_logging(
            level=config.logging.level,
            log_file=config.logging.file,
            log_format=config.logging.format
        )
        
        # 3. Build and return chat service
        return ChatService(config)
