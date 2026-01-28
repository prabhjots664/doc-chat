"""
Final end-to-end test for the new model configuration.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from providers.openrouter_llm import OpenRouterLLMProvider
from providers.voyageai_embedding import VoyageAIEmbeddingProvider
from domain.entities import LLMMessage
from core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(level="INFO")

def test_final_models():
    print("=" * 60)
    print("Testing Final Model Configuration")
    print("=" * 60)
    
    # 1. Test LLM (GLM-4.5-air)
    print("\n1. Testing OpenRouter (z-ai/glm-4.5-air:free)...")
    llm = OpenRouterLLMProvider(api_key=os.getenv("OPENROUTER_API_KEY"))
    msg = [LLMMessage(role="user", content="Say 'System Ready' in 2 words.")]
    resp = llm.generate(messages=msg, max_tokens=10)
    print(f"✅ LLM Response: {resp.content}")
    
    # 2. Test Embedding (voyage-context-3)
    print("\n2. Testing Voyage AI (voyage-context-3)...")
    embedding = VoyageAIEmbeddingProvider(api_key=os.getenv("VOYAGEAI_API_KEY"))
    texts = [["This is a test document.", "It has multiple chunks."]]
    result = embedding.embed(texts, input_type="document")
    print(f"✅ Embedding Results: {len(result.embeddings)} chunks embedded.")
    print(f"   Dimension: {result.dimension}")
    
    print("\n" + "=" * 60)
    print("✅ All systems go!")
    print("=" * 60)

if __name__ == "__main__":
    test_final_models()
