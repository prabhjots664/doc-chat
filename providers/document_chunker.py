"""
Document chunking strategies.
Based on the embed project's chunking implementation.
"""

from abc import ABC, abstractmethod
from typing import List
from domain.entities import DocumentChunk
from core.logging import get_logger

logger = get_logger(__name__)


class IDocumentChunker(ABC):
    """Interface for document chunking strategies."""
    
    @abstractmethod
    def chunk(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Combine or split chunks based on strategy.
        
        Args:
            chunks: List of initial document chunks
            
        Returns:
            List of processed chunks
        """
        pass


class ParagraphChunker(IDocumentChunker):
    """Chunk documents by paragraph with size limits."""
    
    def __init__(
        self,
        min_chunk_size: int = 100,
        max_chunk_size: int = 500,
        overlap_size: int = 50
    ):
        """
        Initialize paragraph chunker.
        
        Args:
            min_chunk_size: Minimum chunk size in characters
            max_chunk_size: Maximum chunk size in characters
            overlap_size: Overlap between chunks in characters
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        logger.info(f"Initialized ParagraphChunker: min={min_chunk_size}, max={max_chunk_size}, overlap={overlap_size}")
    
    def chunk(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Combine chunks respecting size limits."""
        if not chunks:
            return []
        
        result_chunks = []
        current_texts = []
        current_size = 0
        source_metadata = chunks[0].metadata.copy()
        
        for chunk in chunks:
            text = chunk.text
            text_size = len(text)
            
            # If adding this text exceeds max size and we have content, save current chunk
            if current_size + text_size > self.max_chunk_size and current_texts:
                combined_text = " ".join(current_texts)
                result_chunks.append(DocumentChunk(
                    text=combined_text,
                    chunk_index=len(result_chunks),
                    metadata=source_metadata
                ))
                
                # Keep overlap from previous chunk
                if self.overlap_size > 0 and current_texts:
                    overlap_text = current_texts[-1][-self.overlap_size:] if len(current_texts[-1]) > self.overlap_size else current_texts[-1]
                    current_texts = [overlap_text]
                    current_size = len(overlap_text)
                else:
                    current_texts = []
                    current_size = 0
            
            current_texts.append(text)
            current_size += text_size
        
        # Add remaining chunk
        if current_texts:
            combined_text = " ".join(current_texts)
            result_chunks.append(DocumentChunk(
                text=combined_text,
                chunk_index=len(result_chunks),
                metadata=source_metadata
            ))
        
        logger.info(f"Chunked {len(chunks)} elements into {len(result_chunks)} chunks")
        return result_chunks


class TitleChunker(IDocumentChunker):
    """Chunk documents by title/section."""
    
    def __init__(self, max_chunk_size: int = 1000):
        """Initialize title chunker."""
        self.max_chunk_size = max_chunk_size
        logger.info(f"Initialized TitleChunker: max={max_chunk_size}")
    
    def chunk(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Group chunks by title elements."""
        if not chunks:
            return []
        
        result_chunks = []
        current_texts = []
        current_size = 0
        source_metadata = chunks[0].metadata.copy()
        
        for chunk in chunks:
            is_title = chunk.metadata.get('element_type') == 'Title'
            text = chunk.text
            text_size = len(text)
            
            # Start new chunk at titles (if we have content)
            if is_title and current_texts:
                combined_text = " ".join(current_texts)
                result_chunks.append(DocumentChunk(
                    text=combined_text,
                    chunk_index=len(result_chunks),
                    metadata=source_metadata
                ))
                current_texts = []
                current_size = 0
            
            # Also split if too large
            if current_size + text_size > self.max_chunk_size and current_texts:
                combined_text = " ".join(current_texts)
                result_chunks.append(DocumentChunk(
                    text=combined_text,
                    chunk_index=len(result_chunks),
                    metadata=source_metadata
                ))
                current_texts = []
                current_size = 0
            
            current_texts.append(text)
            current_size += text_size
        
        # Add remaining chunk
        if current_texts:
            combined_text = " ".join(current_texts)
            result_chunks.append(DocumentChunk(
                text=combined_text,
                chunk_index=len(result_chunks),
                metadata=source_metadata
            ))
        
        logger.info(f"Chunked {len(chunks)} elements into {len(result_chunks)} chunks")
        return result_chunks


class FixedSizeChunker(IDocumentChunker):
    """
    A simple yet robust chunker that splits text into fixed-size segments.
    This ensures that even massive single-block documents are properly segmented.
    """
    
    def __init__(self, max_chunk_size: int = 500, overlap_size: int = 50):
        """
        Initialize fixed-size chunker.
        
        Args:
            max_chunk_size: Maximum words per chunk
            overlap_size: Overlap between chunks (in words)
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        logger.info(f"Initialized FixedSizeChunker (Word-based): max={max_chunk_size} words, overlap={overlap_size} words")
    
    def chunk(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Split all text into fixed-size segments based on word count."""
        if not chunks:
            return []
            
        # 1. Join all text and split into words
        full_text = " ".join([c.text for c in chunks])
        source_metadata = chunks[0].metadata.copy()
        
        if not full_text:
            return []
            
        words = full_text.split()
        num_words = len(words)
        result_chunks = []
        start = 0
        
        # 2. Slice the word list using a sliding window
        while start < num_words:
            end = min(start + self.max_chunk_size, num_words)
            
            # Extract word slice and rejoin
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            result_chunks.append(DocumentChunk(
                text=chunk_text.strip(),
                chunk_index=len(result_chunks),
                metadata=source_metadata
            ))
            
            # Move start forward, leaving space for word overlap
            if end == num_words:
                break
            
            # Ensure start actually moves forward
            next_start = end - self.overlap_size
            if next_start <= start:
                start = end
            else:
                start = next_start
                
        logger.info(f"FixedSizeChunker: Split {num_words} words into {len(result_chunks)} chunks")
        return result_chunks
