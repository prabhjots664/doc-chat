"""
Document Processing Service.
Orchestrates document loading, chunking, embedding, and storage.
"""

from typing import List, Union, Dict, Any
from pathlib import Path

from providers.document_loader import LightweightDocumentLoader
from providers.document_chunker import ParagraphChunker, TitleChunker, FixedSizeChunker
from providers.voyageai_embedding import VoyageAIEmbeddingProvider
from providers.qdrant_adapter import QdrantAdapter
from domain.entities import DocumentChunk, Document
from core.exceptions import DocumentProcessingError
from core.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessingService:
    """Service for processing and storing documents."""
    
    def __init__(
        self,
        embedding_provider: VoyageAIEmbeddingProvider,
        vector_store: QdrantAdapter,
        collection_name: str = "documents",
        chunk_strategy: str = "by_paragraph",
        min_chunk_size: int = 100,
        max_chunk_size: int = 500,
        overlap_size: int = 50
    ):
        """
        Initialize document processing service.
        
        Args:
            embedding_provider: Embedding provider instance
            vector_store: Vector store instance
            collection_name: Name of the collection to store documents
            chunk_strategy: Chunking strategy ("by_paragraph" or "by_title")
            min_chunk_size: Minimum chunk size
            max_chunk_size: Maximum chunk size
            overlap_size: Overlap between chunks
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.collection_name = collection_name
        self.MAX_CHUNKS = 1000  # Guardrail: Maximum chunks per document
        
        # Initialize loader
        self.loader = LightweightDocumentLoader()
        
        # Initialize chunker based on strategy
        if chunk_strategy == "by_paragraph":
            self.chunker = ParagraphChunker(min_chunk_size, max_chunk_size, overlap_size)
        elif chunk_strategy == "by_title":
            self.chunker = TitleChunker(max_chunk_size)
        elif chunk_strategy == "fixed_size":
            self.chunker = FixedSizeChunker(max_chunk_size, overlap_size)
        else:
            raise ValueError(f"Unknown chunk strategy: {chunk_strategy}")
        
        # Ensure collection exists
        self._ensure_collection()
        
        logger.info(f"Initialized DocumentProcessingService: collection={collection_name}, strategy={chunk_strategy}")
    
    def _ensure_collection(self):
        """Ensure the collection exists in the vector store."""
        try:
            # Try to get collection info
            self.vector_store.get_collection_info(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            # Create collection if it doesn't exist
            dimension = self.embedding_provider.get_dimension()
            self.vector_store.create_collection(
                collection_name=self.collection_name,
                vector_size=dimension,
                distance_metric="cosine"
            )
            logger.info(f"Created collection '{self.collection_name}'")
    
    def process_document(self, file_path: Union[str, Path]) -> Document:
        """
        Process a document: load, chunk, embed, and store.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document object with processing metadata
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        try:
            file_path = Path(file_path)
            logger.info(f"Processing document: {file_path}")
            
            # 1. Load document
            raw_chunks = self.loader.load(file_path)
            logger.info(f"Loaded {len(raw_chunks)} raw chunks")
            
            # 2. Apply chunking strategy
            processed_chunks = self.chunker.chunk(raw_chunks)
            logger.info(f"Processed into {len(processed_chunks)} chunks")
            
            if not processed_chunks:
                raise DocumentProcessingError(f"No chunks generated from {file_path}")
            
            # Guardrail: Check chunk count
            if len(processed_chunks) > self.MAX_CHUNKS:
                raise DocumentProcessingError(
                    f"Document produced too many chunks: {len(processed_chunks)}. "
                    f"Max allowed: {self.MAX_CHUNKS}"
                )
            
            # 3. Generate embeddings
            texts = [chunk.text for chunk in processed_chunks]
            embedding_result = self.embedding_provider.embed(texts, input_type="document")
            logger.info(f"Generated {len(embedding_result.embeddings)} embeddings")
            
            # 4. Store in vector database
            payloads = [
                {
                    'text': chunk.text,
                    'metadata': chunk.metadata
                }
                for chunk in processed_chunks
            ]
            
            self.vector_store.upsert(
                collection_name=self.collection_name,
                vectors=embedding_result.embeddings,
                payloads=payloads
            )
            logger.info(f"Stored {len(processed_chunks)} chunks in vector store")
            
            # 5. Return document object
            document = Document(
                file_path=str(file_path),
                chunks=processed_chunks,
                metadata={
                    'num_chunks': len(processed_chunks),
                    'total_tokens': embedding_result.tokens_used,
                    'file_type': file_path.suffix.lower()
                }
            )
            
            logger.info(f"Successfully processed document: {file_path}")
            return document
            
        except Exception as e:
            error_msg = f"Failed to process document {file_path}: {str(e)}"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return self.vector_store.get_collection_info(self.collection_name)
