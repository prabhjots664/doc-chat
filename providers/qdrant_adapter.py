"""
Qdrant vector store adapter implementation.
Based on the embed project's document_search_qdrant.py pattern.
"""

import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import time

from interfaces.vector_store import IVectorStore
from domain.entities import SearchResult
from core.exceptions import ProviderError
from core.logging import get_logger

logger = get_logger(__name__)


class QdrantAdapter(IVectorStore):
    """Qdrant vector store implementation."""
    
    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize Qdrant client.
        
        Args:
            url: Full Qdrant URL (e.g., http://localhost:6333 or https://...)
            api_key: API Key for authorization
            timeout: Connection timeout in seconds
            max_retries: Maximum connection retry attempts
        """
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        logger.info(f"Initializing Qdrant client at {self.url}")
        self.client = self._init_client()
    
    def _init_client(self) -> QdrantClient:
        """Initialize Qdrant client with retry logic."""
        for attempt in range(self.max_retries):
            try:
                client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=self.timeout
                )
                # Test connection
                client.get_collections()
                logger.info(f"Successfully connected to Qdrant at {self.url}")
                return client
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    error_msg = f"Could not connect to Qdrant at {self.url} after {self.max_retries} attempts"
                    logger.error(error_msg)
                    logger.error("Please make sure Qdrant is running. You can start it with:")
                    logger.error("docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
                    raise ProviderError(error_msg)
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "cosine"
    ) -> bool:
        """Create a new collection."""
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if collection_name in collection_names:
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Map distance metric
            distance_map = {
                "cosine": Distance.COSINE,
                "euclidean": Distance.EUCLID,
                "dot": Distance.DOT
            }
            distance = distance_map.get(distance_metric.lower(), Distance.COSINE)
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            logger.info(f"Created collection: {collection_name} (size={vector_size}, distance={distance_metric})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {str(e)}")
            raise ProviderError(f"Failed to create collection: {str(e)}")
    
    def upsert(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Insert or update vectors in the collection."""
        try:
            if len(vectors) != len(payloads):
                raise ValueError("Number of vectors must match number of payloads")
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            # Create points
            points = [
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
            
            logger.info(f"Upserted {len(points)} points to collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting to collection '{collection_name}': {str(e)}")
            raise ProviderError(f"Failed to upsert vectors: {str(e)}")
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        try:
            # Prepare search parameters
            search_params = {
                'collection_name': collection_name,
                'query': query_vector,
                'limit': limit
            }
            
            # Add filter if provided
            if filter_conditions:
                # Simple filter implementation
                # Can be extended for more complex filters
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if must_conditions:
                    search_params['query_filter'] = Filter(must=must_conditions)
            
            # Perform search using modern query_points API
            response = self.client.query_points(**search_params)
            search_results = response.points
            
            # Convert to SearchResult objects
            results = [
                SearchResult(
                    text=result.payload.get('text', ''),
                    score=result.score,
                    metadata=result.payload
                )
                for result in search_results
            ]
            
            logger.info(f"Found {len(results)} results in collection '{collection_name}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching collection '{collection_name}': {str(e)}")
            raise ProviderError(f"Failed to search vectors: {str(e)}")
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {str(e)}")
            raise ProviderError(f"Failed to delete collection: {str(e)}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name)
            count = self.client.count(collection_name)
            
            return {
                'name': collection_name,
                'vectors_count': count.count,
                'status': info.status,
                'vector_size': info.config.params.vectors.size,
                'distance': str(info.config.params.vectors.distance)
            }
        except Exception as e:
            logger.error(f"Error getting info for collection '{collection_name}': {str(e)}")
            raise ProviderError(f"Failed to get collection info: {str(e)}")
    
    def validate_connection(self) -> bool:
        """Validate that the vector store is accessible."""
        try:
            self.client.get_collections()
            logger.info("Qdrant connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Qdrant connection validation failed: {str(e)}")
            raise ProviderError(f"Connection validation failed: {str(e)}")
