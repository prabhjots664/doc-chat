from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import os

client = QdrantClient(host="localhost", port=6333)

def test_qdrant_search():
    print("Testing Qdrant search...")
    try:
        # Create collection if not exists
        if not client.collection_exists("test_search"):
            client.create_collection(
                "test_search",
                vectors_config=VectorParams(size=4, distance=Distance.COSINE)
            )
            client.upsert(
                "test_search",
                points=[
                    PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"text": "hello"}),
                ]
            )
        
        # Try search
        print("Calling client.search...")
        results = client.search(
            collection_name="test_search",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=1
        )
        print(f"Search success: {results}")
    except Exception as e:
        print(f"Search failed: {e}")
        print("Checking available methods again...")
        print([m for m in dir(client) if not m.startswith('_')])

if __name__ == "__main__":
    test_qdrant_search()
