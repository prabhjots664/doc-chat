"""
Chat Service.
Orchestrates the overall chat experience.
"""

import os
from typing import List, Dict, Any, Optional
from domain.entities import ChatMessage, LLMMessage, LLMResponse
from providers.openrouter_llm import OpenRouterLLMProvider
from providers.voyageai_embedding import VoyageAIEmbeddingProvider
from providers.qdrant_adapter import QdrantAdapter
from services.rag_pipeline_service import RAGPipelineService
from services.document_processing_service import DocumentProcessingService
from core.config import Config
from core.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for managing the chat application."""
    
    def __init__(self, config: Config):
        """
        Initialize the chat service.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Initialize providers
        self.llm = OpenRouterLLMProvider(
            api_key=config.get_api_key(config.llm.api_key_env),
            model=config.llm.model,
            base_url=config.llm.base_url,
            verify_ssl=config.llm.verify_ssl
        )
        
        self.embedding = VoyageAIEmbeddingProvider(
            api_key=config.get_api_key(config.embeddings.api_key_env),
            model=config.embeddings.model,
            verify_ssl=config.embeddings.verify_ssl
        )
        
        self.vector_store = QdrantAdapter(
            url=config.vector_db.url,
            api_key=config.get_api_key(config.vector_db.api_key_env) if os.getenv(config.vector_db.api_key_env) else None,
            timeout=config.vector_db.timeout
        )
        
        # Initialize services
        self.doc_processing = DocumentProcessingService(
            embedding_provider=self.embedding,
            vector_store=self.vector_store,
            collection_name=config.vector_db.collection_name,
            chunk_strategy=config.chunking.strategy,
            max_chunk_size=config.chunking.max_chunk_size,
            overlap_size=config.chunking.overlap_size
        )
        
        self.rag_pipeline = RAGPipelineService(
            llm_provider=self.llm,
            embedding_provider=self.embedding,
            vector_store=self.vector_store,
            collection_name=config.vector_db.collection_name
        )
        
        # Persistent storage for chat sessions
        self.sessions: Dict[str, List[LLMMessage]] = {}
        
        logger.info("ChatService successfully initialized")
    
    def chat(
        self,
        session_id: str,
        user_message: str,
        use_rag: bool = True
    ) -> ChatMessage:
        """
        Process a user message and return a response.
        
        Args:
            session_id: Unique identifier for the chat session
            user_message: User's input text
            use_rag: Whether to use RAG or direct LLM
            
        Returns:
            ChatMessage containing the response
        """
        try:
            # 1. Get or create session history
            history = self.sessions.get(session_id, [])
            
            # 2. Generate response
            if use_rag:
                response = self.rag_pipeline.query(
                    user_query=user_message,
                    chat_history=history
                )
            else:
                messages = history + [LLMMessage(role="user", content=user_message)]
                response = self.llm.generate(messages=messages)
            
            # 3. Update history
            history.append(LLMMessage(role="user", content=user_message))
            history.append(LLMMessage(role="assistant", content=response.content))
            self.sessions[session_id] = history
            
            # 4. Convert to domain entity
            return ChatMessage(
                role="assistant",
                content=response.content,
                metadata=response.metadata
            )
            
        except Exception as e:
            logger.error(f"Error in chat service for session {session_id}: {str(e)}")
            return ChatMessage(
                role="assistant",
                content=f"Error: {str(e)}",
                metadata={'error': True}
            )
    
    def ingest_document(self, file_path: str) -> bool:
        """Ingest a document into the system."""
        try:
            self.doc_processing.process_document(file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {str(e)}")
            return False
            
    def clear_session(self, session_id: str):
        """Clear chat history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"Cleared session {session_id}")
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get system health and status information."""
        try:
            db_info = self.vector_store.get_collection_info(self.config.vector_db.collection_name)
            # Get actual runtime model from the RAG pipeline's LLM instance
            actual_model = getattr(self.rag_pipeline.micro_llm, 'model', self.config.llm.model)
            return {
                'status': 'healthy',
                'vector_db': db_info,
                'llm_model': actual_model,
                'embedding_model': self.config.embeddings.model
            }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e)
            }
