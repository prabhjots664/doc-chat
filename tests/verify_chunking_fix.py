"""
Verification script for the chunking fix.
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from factories.service_factory import ServiceFactory
from core.config import Config

def verify_chunking():
    load_dotenv()
    
    # 1. Initialize config and service
    config = Config()
    # Force fixed_size strategy for verification
    config.chunking.strategy = "fixed_size"
    config.chunking.max_chunk_size = 500
    
    chat_service = ServiceFactory.create_chat_service()
    
    # 2. Create a "large" mock document (~1200 words)
    mock_content = "word " * 1200
    test_file = Path("tests/large_test_doc.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(mock_content)
    
    print(f"File size: {len(mock_content)} chars")
    
    # 3. Ingest
    print("\nIngesting document...")
    success = chat_service.ingest_document(str(test_file))
    
    if success:
        print("✅ Ingestion successful!")
        
        # 4. Check system status for chunk count
        status = chat_service.get_system_status()
        chunk_count = status.get('vector_db', {}).get('vectors_count', 0)
        print(f"✅ Total chunks in Qdrant: {chunk_count}")
        
        if chunk_count > 1:
            print(f"🔥 Success! Document was split into multiple chunks.")
        else:
            print(f"⚠️ Warning: Document is still only 1 chunk.")
    else:
        print("❌ Ingestion failed.")
        
    # Cleanup
    if test_file.exists():
        test_file.unlink()

if __name__ == "__main__":
    verify_chunking()
