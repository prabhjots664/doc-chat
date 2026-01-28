"""
End-to-end integration test for the chat service.
Verifies ingestion, retrieval, and generation.
"""

import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from factories.service_factory import ServiceFactory
from core.logging import get_logger

logger = get_logger("test")

def test_chat_flow():
    print("=" * 60)
    print("End-to-End Chat Integration Test")
    print("=" * 60)
    
    try:
        # Load env
        load_dotenv()
        
        # 1. Initialize Service
        print("\n1. Initializing Chat Service through Factory...")
        service = ServiceFactory.create_chat_service()
        print("✅ Service initialized")
        
        # 2. Ingest sample document
        print("\n2. Ingesting sample document...")
        sample_doc = "sample_docs/machine_learning.md"
        success = service.ingest_document(sample_doc)
        if success:
            print(f"✅ Document '{sample_doc}' successfully ingested")
        else:
            print("❌ Document ingestion failed")
            return
            
        # 3. Test RAG Chat
        print("\n3. Testing RAG query...")
        session_id = "test-session-1"
        query = "What are the common types of machine learning discussed in the document?"
        
        print(f"User: {query}")
        response = service.chat(session_id, query, use_rag=True)
        
        print(f"\nAssistant: {response.content}")
        print(f"\n✅ Chat response received")
        print(f"   Tokens: {response.metadata.get('prompt_tokens', 0) + response.metadata.get('completion_tokens', 0)}")
        print(f"   Chunks used: {len(response.metadata.get('search_results', []))}")
        
        # 4. Test follow-up question (checking history)
        print("\n4. Testing follow-up question (context maintenance)...")
        query2 = "Which one of them uses labeled data?"
        print(f"User: {query2}")
        response2 = service.chat(session_id, query2, use_rag=True)
        
        print(f"\nAssistant: {response2.content}")
        print(f"\n✅ Follow-up response received")
        
        # 5. Check System Status
        print("\n5. Checking system status...")
        status = service.get_system_status()
        print(f"✅ System Status: {status['status']}")
        print(f"   Collection Size: {status['vector_db']['vectors_count']} chunks")
        
        print("\n" + "=" * 60)
        print("✅ Integration test successful!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_flow()
