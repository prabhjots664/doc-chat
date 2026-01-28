"""
Core configuration module for doc-chat system.
Loads configuration from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = "openrouter"
    model: str
    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = "https://openrouter.ai/api/v1"
    temperature: float = 0.7
    max_tokens: int = 4000
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    verify_ssl: bool = Field(default_factory=lambda: os.getenv("VERIFY_SSL", "True").lower() == "true")


class EmbeddingConfig(BaseModel):
    """Embedding provider configuration."""
    provider: str = "voyageai"
    model: str = "voyage-context-3"
    api_key_env: str = "VOYAGEAI_API_KEY"
    dimension: int = 1024
    verify_ssl: bool = Field(default_factory=lambda: os.getenv("VERIFY_SSL", "True").lower() == "true")


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    provider: str = "qdrant"
    url: str = Field(default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"))
    api_key_env: Optional[str] = "QDRANT_API_KEY"
    timeout: int = 10
    collection_name: str = "documents"


class ChunkingConfig(BaseModel):
    """Document chunking configuration."""
    strategy: str = "fixed_size"  # by_title, by_paragraph, by_sentence, fixed_size
    min_chunk_size: int = 100
    max_chunk_size: int = 500
    overlap_size: int = 50


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    file: str = "document_chat.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class AppConfig(BaseModel):
    """Application configuration."""
    upload_dir: str = "uploads"
    environment: str = "development"


class Config:
    """Main configuration class that loads and manages all settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config YAML file. If None, uses default.
        """
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_path = config_path or self.config_dir / "config.yaml"
        
        # Load configuration
        self._config = self._load_config()
        
        # Initialize typed configs
        self.llm = LLMConfig(**self._config.get("llm", {}))
        self.embeddings = EmbeddingConfig(**self._config.get("embeddings", {}))
        self.vector_db = VectorDBConfig(**self._config.get("vector_db", {}))
        self.chunking = ChunkingConfig(**self._config.get("chunking", {}))
        self.logging = LoggingConfig(**self._config.get("logging", {}))
        self.app = AppConfig(**self._config.get("app", {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            # Return default configuration
            return self._get_default_config()
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Load environment-specific overrides
        env = os.getenv("APP_ENV", "development")
        env_config_path = self.config_dir / f"{env}.yaml"
        
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                config = self._merge_configs(config, env_config)
        
        # Override with environment variables
        config = self._apply_env_overrides(config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "llm": {
                "provider": "openrouter",
                "model": os.getenv("OPENROUTER_MODEL"),  # Must come from .env
                "api_key_env": "OPENROUTER_API_KEY",
                "base_url": "https://openrouter.ai/api/v1",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "embeddings": {
                "provider": "voyageai",
                "model": "voyage-context-3",
                "api_key_env": "VOYAGEAI_API_KEY",
                "dimension": 1024
            },
            "vector_db": {
                "provider": "qdrant",
                "url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                "api_key_env": os.getenv("QDRANT_API_KEY_ENV", "QDRANT_API_KEY"),
                "timeout": int(os.getenv("QDRANT_TIMEOUT", 10)),
                "collection_name": os.getenv("COLLECTION_NAME", "documents")
            },
            "chunking": {
                "strategy": os.getenv("CHUNK_STRATEGY", "fixed_size"),
                "min_chunk_size": int(os.getenv("MIN_CHUNK_SIZE", 100)),
                "max_chunk_size": int(os.getenv("MAX_CHUNK_SIZE", 500)),
                "overlap_size": int(os.getenv("OVERLAP_SIZE", 50))
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file": os.getenv("LOG_FILE", "document_chat.log"),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "app": {
                "upload_dir": os.getenv("UPLOAD_DIR", "uploads"),
                "environment": os.getenv("APP_ENV", "development")
            }
        }
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    def _apply_env_overrides(self, config: Dict) -> Dict:
        """Apply environment variable overrides."""
        # LLM overrides
        if "llm" in config:
            if os.getenv("LLM_PROVIDER"):
                config["llm"]["provider"] = os.getenv("LLM_PROVIDER")
            if os.getenv("LLM_MODEL"):
                config["llm"]["model"] = os.getenv("LLM_MODEL")
            if os.getenv("OPENROUTER_MODEL"):
                config["llm"]["model"] = os.getenv("OPENROUTER_MODEL")
                print(f"DEBUG: Applied OPENROUTER_MODEL override: {config['llm']['model']}")
        
        # Vector DB overrides
        if "vector_db" in config:
            if os.getenv("QDRANT_URL"):
                config["vector_db"]["url"] = os.getenv("QDRANT_URL")
            if os.getenv("COLLECTION_NAME"):
                config["vector_db"]["collection_name"] = os.getenv("COLLECTION_NAME")
        
        # Chunking overrides
        if "chunking" in config:
            if os.getenv("CHUNK_STRATEGY"):
                config["chunking"]["strategy"] = os.getenv("CHUNK_STRATEGY")
            if os.getenv("MIN_CHUNK_SIZE"):
                config["chunking"]["min_chunk_size"] = int(os.getenv("MIN_CHUNK_SIZE"))
            if os.getenv("MAX_CHUNK_SIZE"):
                config["chunking"]["max_chunk_size"] = int(os.getenv("MAX_CHUNK_SIZE"))
            if os.getenv("OVERLAP_SIZE"):
                config["chunking"]["overlap_size"] = int(os.getenv("OVERLAP_SIZE"))
        
        return config
    
    def get_api_key(self, env_var: str) -> str:
        """
        Get API key from environment variable.
        
        Args:
            env_var: Name of environment variable
            
        Returns:
            API key value
            
        Raises:
            ValueError: If API key not found
        """
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {env_var}")
        return api_key
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., "llm.model")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
