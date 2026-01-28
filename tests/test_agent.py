import os
import logging
from core.config import Config
from factories.service_factory import ServiceFactory
from services.rag_pipeline_service import RAGPipelineService

# Setup logging to console - verifying the user's request for visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_agent():
    print("--- 🚀 Starting Agent Diagnostic ---")
    
    # Initialize services
    chat_service = ServiceFactory.create_chat_service()
    rag = chat_service.rag_pipeline
    
    # Test Query
    query = "what assignments are given to the lead ai engineer"
    print(f"\n❓ User Query: {query}\n")
    
    try:
        response = rag.query(query)
        print("\n--- ✅ Agent Execution Complete ---")
        print(f"Final Answer: {response.content}")
        print(f"Metadata: {response.metadata}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_agent()
