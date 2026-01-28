# Implementation Guide - Quick Reference

## Overview

This document provides a quick reference for implementing the RAG Document Chat System based on the architecture defined in `ARCHITECTURE.md`.

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Implement configuration system
- [ ] Define all interfaces
- [ ] Set up logging and error handling
- [ ] Create base factories

### Phase 2: Core Providers (Week 2)
- [ ] Implement OpenRouter LLM adapter
- [ ] Implement Voyage AI embedding adapter
- [ ] Implement Qdrant vector store adapter
- [ ] Implement Unstructured document loader
- [ ] Write unit tests for all providers

### Phase 3: Document Processing (Week 3)
- [ ] Implement chunking strategies
- [ ] Implement document processing service
- [ ] Create document processing pipeline
- [ ] Test with various document formats
- [ ] Add progress tracking

### Phase 4: RAG Pipeline (Week 4)
- [ ] Implement RAG pipeline service
- [ ] Implement chat service
- [ ] Add guardrails manager
- [ ] Integration testing
- [ ] Performance optimization

### Phase 5: UI & Polish (Week 5)
- [ ] Build Streamlit interface
- [ ] Add file upload functionality
- [ ] Create chat interface
- [ ] Add settings panel
- [ ] Error handling in UI

### Phase 6: Production Ready (Week 6)
- [ ] Docker containerization
- [ ] Monitoring and metrics
- [ ] Health checks
- [ ] Documentation
- [ ] Deployment guides

---

## Quick Start Implementation Order

### 1. Start with Interfaces

**Why first?** Interfaces define the contract. Once interfaces are defined, multiple team members can work in parallel on different implementations.

```python
# interfaces/llm_provider.py - Define first
# interfaces/embedding_provider.py - Define first
# interfaces/vector_store.py - Define first
```

### 2. Configuration System

**Why second?** Everything depends on configuration. Get this right early.

```python
# core/config.py
# config/config.yaml
# .env.example
```

### 3. Simplest Provider First

**Why?** Validate the interface design with a real implementation.

Start with: `QdrantVectorStoreAdapter` (simplest, local)

### 4. Add External Providers

**Order**: 
1. VoyageAI (needed for embeddings)
2. OpenRouter (needed for chat)

### 5. Document Processing

**Order**:
1. Loader (Unstructured)
2. Chunker (start with paragraph strategy)
3. Processing Service

### 6. Services

**Order**:
1. DocumentProcessingService
2. RAGPipelineService
3. ChatService
4. GuardrailsManager

---

## Code Examples for Critical Components

### Example 1: Factory Pattern Usage

```python
# app_initializer.py
class ApplicationInitializer:
    """Initialize application with DI from config"""
    
    @staticmethod
    def initialize() -> ChatService:
        # Load config
        config = Config()
        
        # Create providers via factories
        llm_provider = LLMProviderFactory.create(
            provider_type=config.get("llm.provider"),
            config={
                "api_key": config.get_api_key(
                    config.get("llm.api_key_env")
                ),
                "model": config.get("llm.model"),
                "site_url": config.get("llm.site_url"),
                "site_name": config.get("llm.site_name")
            }
        )
        
        embedding_provider = EmbeddingProviderFactory.create(
            provider_type=config.get("embeddings.provider"),
            config={
                "api_key": config.get_api_key(
                    config.get("embeddings.api_key_env")
                ),
                "model": config.get("embeddings.model"),
                "dimension": config.get("embeddings.dimension")
            }
        )
        
        vector_store = VectorStoreFactory.create(
            provider_type=config.get("vector_db.provider"),
            config={
                "host": config.get("vector_db.host"),
                "port": config.get("vector_db.port")
            }
        )
        
        # Initialize services
        rag_pipeline = RAGPipelineService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            llm_provider=llm_provider,
            config=config
        )
        
        guardrails = GuardrailsManager(config)
        
        chat_service = ChatService(
            llm_provider=llm_provider,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            guardrails=guardrails,
            rag_pipeline=rag_pipeline,
            config=config
        )
        
        return chat_service
```

### Example 2: Error Handling Pattern

```python
# core/exceptions.py
class DocumentChatException(Exception):
    """Base exception for all custom exceptions"""
    pass

class ProviderError(DocumentChatException):
    """Provider-related errors"""
    pass

class ValidationError(DocumentChatException):
    """Input validation errors"""
    pass

class ProcessingError(DocumentChatException):
    """Document processing errors"""
    pass

# Usage in provider
class OpenRouterLLMAdapter(ILLMProvider):
    def generate(self, messages, **kwargs):
        try:
            response = requests.post(...)
            response.raise_for_status()
            return self._parse_response(response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API failed: {e}")
            raise ProviderError(f"LLM generation failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error in LLM generation")
            raise ProviderError(f"Unexpected error: {e}")
```

### Example 3: Logging Pattern

```python
# core/logging.py
import structlog
import logging
from pathlib import Path

def setup_logging(config):
    """Setup structured logging"""
    
    # Create logs directory
    log_dir = Path(config.get("logging.file")).parent
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure Python logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, config.get("logging.level")),
        handlers=[
            logging.FileHandler(config.get("logging.file")),
            logging.StreamHandler()
        ]
    )

# Usage in code
logger = structlog.get_logger()

logger.info(
    "document_processed",
    document_id=doc_id,
    chunks=25,
    processing_time_ms=1234
)
```

### Example 4: Testing Pattern

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing"""
    mock = Mock(spec=ILLMProvider)
    mock.generate.return_value = LLMResponse(
        content="Test response",
        model="test-model",
        tokens_used=100,
        finish_reason="stop",
        metadata={}
    )
    mock.get_provider_name.return_value = "Mock LLM"
    return mock

@pytest.fixture
def mock_embedding_provider():
    """Mock embedding provider for testing"""
    mock = Mock(spec=IEmbeddingProvider)
    mock.embed.return_value = EmbeddingResult(
        embeddings=np.random.rand(2, 1024),
        model="test-model",
        dimension=1024,
        tokens_used=50,
        metadata={}
    )
    return mock

@pytest.fixture
def chat_service(mock_llm_provider, mock_embedding_provider):
    """Create chat service with mocked dependencies"""
    return ChatService(
        llm_provider=mock_llm_provider,
        embedding_provider=mock_embedding_provider,
        vector_store=Mock(spec=IVectorStore),
        guardrails=Mock(spec=GuardrailsManager),
        rag_pipeline=Mock(spec=RAGPipelineService),
        config=Mock()
    )

# Test usage
def test_chat_basic(chat_service):
    response = chat_service.chat("Hello", [])
    assert response is not None
    assert len(response.content) > 0
```

---

## Key Design Decisions - Quick Reference

### Why Interfaces?

**Benefits:**
- Multiple implementations can coexist
- Easy to swap providers without changing code
- Facilitates testing with mocks
- Clear contracts between components
- Enables parallel development

**Example:**
```python
# Can swap this:
llm = OpenRouterLLMAdapter(...)

# With this (no other code changes):
llm = LocalLLMAdapter(...)

# Or this:
llm = MockLLMProvider()  # For testing
```

### Why Factories?

**Benefits:**
- Centralize object creation logic
- Hide complex initialization
- Enable configuration-based creation
- Reduce coupling

**Example:**
```python
# Instead of:
if config.provider == "openrouter":
    llm = OpenRouterLLMAdapter(...)
elif config.provider == "local":
    llm = LocalLLMAdapter(...)

# Use:
llm = LLMProviderFactory.create(
    provider_type=config.provider,
    config=config
)
```

### Why Dependency Injection?

**Benefits:**
- Testability (inject mocks)
- Flexibility (swap implementations)
- Clear dependencies
- No hidden coupling

**Example:**
```python
# Good: Dependencies explicit and injected
class ChatService:
    def __init__(
        self,
        llm_provider: ILLMProvider,  # Explicit dependency
        vector_store: IVectorStore    # Explicit dependency
    ):
        self.llm = llm_provider
        self.vector_store = vector_store

# Bad: Hidden dependencies
class ChatService:
    def __init__(self):
        self.llm = OpenRouterLLMAdapter()  # Hidden, hardcoded
        self.vector_store = QdrantClient()  # Can't test
```

---

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Leaky Abstractions

**Bad:**
```python
class ILLMProvider(ABC):
    @abstractmethod
    def generate_openai_format(self, messages):  # Too specific!
        pass
```

**Good:**
```python
class ILLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[LLMMessage]):  # Generic
        pass
```

### ❌ Pitfall 2: Fat Interfaces

**Bad:**
```python
class IProvider(ABC):
    # LLM methods
    def generate(self): pass
    # Embedding methods
    def embed(self): pass
    # Vector store methods
    def search(self): pass
    # Too many responsibilities!
```

**Good:**
```python
# Separate interfaces
class ILLMProvider(ABC): ...
class IEmbeddingProvider(ABC): ...
class IVectorStore(ABC): ...
```

### ❌ Pitfall 3: Implementation Details in Interface

**Bad:**
```python
@abstractmethod
def get_openai_client(self):  # Implementation detail leaked
    pass
```

**Good:**
```python
@abstractmethod
def generate(self, messages):  # Abstract behavior
    pass
```

### ❌ Pitfall 4: Not Using Type Hints

**Bad:**
```python
def process(self, data):  # What is data?
    return result  # What is result?
```

**Good:**
```python
def process(self, data: List[str]) -> ProcessingResult:
    return ProcessingResult(...)
```

### ❌ Pitfall 5: Mixing Concerns

**Bad:**
```python
class ChatService:
    def chat(self, message):
        # Business logic
        result = self.rag_pipeline.execute(message)
        
        # UI concerns (wrong layer!)
        print("Response:", result)
        save_to_file(result)
        
        return result
```

**Good:**
```python
class ChatService:
    def chat(self, message):
        # Only business logic
        result = self.rag_pipeline.execute(message)
        logger.info("chat_completed", tokens=result.tokens)
        return result

# UI layer handles presentation
def display_response(response):
    print("Response:", response)
```

---

## Development Workflow

### 1. Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/semantic-chunker

# 2. Write interface (if new)
# interfaces/document_chunker.py

# 3. Write tests first (TDD)
# tests/unit/test_semantic_chunker.py

# 4. Implement feature
# providers/semantic_chunker.py

# 5. Run tests
pytest tests/unit/test_semantic_chunker.py -v

# 6. Check coverage
pytest --cov=providers.semantic_chunker tests/

# 7. Run linter
black providers/semantic_chunker.py
flake8 providers/semantic_chunker.py
mypy providers/semantic_chunker.py

# 8. Integration test
pytest tests/integration/ -v

# 9. Commit
git add .
git commit -m "feat: add semantic chunking strategy"

# 10. Push and create PR
git push origin feature/semantic-chunker
```

### 2. Code Review Checklist

- [ ] Follows interface contracts
- [ ] Has unit tests (>80% coverage)
- [ ] Has integration tests (if applicable)
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] Error handling present
- [ ] Logging added for key operations
- [ ] No hardcoded values
- [ ] Configuration-driven
- [ ] Follows SOLID principles

### 3. Testing Checklist

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Code coverage > 80%
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] Mocking done correctly
- [ ] No flaky tests

---

## Performance Optimization Tips

### 1. Batch Operations

**Before:**
```python
for text in texts:
    embedding = embedding_provider.embed_single(text)
    embeddings.append(embedding)
```

**After:**
```python
# Much faster - single API call
embeddings = embedding_provider.embed(texts)
```

### 2. Connection Pooling

```python
class QdrantVectorStoreAdapter:
    def __init__(self, host, port):
        # Reuse client across requests
        self.client = QdrantClient(host=host, port=port)
        
    # Don't create new client in each method!
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> np.ndarray:
    return embedding_provider.embed_single(text)
```

### 4. Async Operations (Future)

```python
async def process_documents_parallel(files):
    tasks = [process_document(file) for file in files]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Debugging Tips

### 1. Enable Debug Logging

```yaml
# config/development.yaml
logging:
  level: "DEBUG"
```

### 2. Use Breakpoints

```python
import pdb; pdb.set_trace()  # Debugger breakpoint

# Or in VS Code: Just click line number to add breakpoint
```

### 3. Log Request/Response

```python
logger.debug(
    "llm_request",
    model=self.model,
    messages=messages,
    temperature=temperature
)

response = self._make_request(...)

logger.debug(
    "llm_response",
    tokens=response.tokens_used,
    finish_reason=response.finish_reason
)
```

### 4. Use Health Checks

```python
# Check each component
chat_service.validate_providers()
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] No linter errors
- [ ] Documentation updated
- [ ] API keys in Secrets Manager
- [ ] Environment configs ready
- [ ] Docker build successful
- [ ] Health checks working
- [ ] Monitoring configured
- [ ] Logging configured

### Deployment

- [ ] Start Qdrant container
- [ ] Run database migrations (if any)
- [ ] Start application container
- [ ] Verify health checks
- [ ] Run smoke tests
- [ ] Monitor logs for errors
- [ ] Check metrics dashboard

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify functionality
- [ ] Update documentation
- [ ] Notify team

---

## Useful Commands

### Docker

```bash
# Build image
docker build -t doc-chat:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all
docker-compose down

# Clean volumes
docker-compose down -v
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_chunker.py -v

# Run with coverage
pytest --cov=services --cov-report=html

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_embedding"
```

### Linting

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Run all checks
pre-commit run --all-files
```

---

## Quick Reference: Class Hierarchy

```
Interfaces (ABC)
│
├── ILLMProvider
│   ├── OpenRouterLLMAdapter
│   └── LocalLLMAdapter
│
├── IEmbeddingProvider
│   ├── VoyageAIEmbeddingAdapter
│   └── LocalEmbeddingProvider
│
├── IVectorStore
│   ├── QdrantVectorStoreAdapter
│   └── FAISSVectorStoreAdapter
│
├── IDocumentLoader
│   └── UnstructuredDocumentLoader
│
└── IDocumentChunker
    ├── ParagraphChunker
    ├── SentenceChunker
    └── SemanticChunker

Services (Business Logic)
│
├── ChatService
├── DocumentProcessingService
├── RAGPipelineService
└── GuardrailsManager

Factories
│
├── LLMProviderFactory
├── EmbeddingProviderFactory
└── VectorStoreFactory
```

---

## Next Steps After Architecture Review

1. **Setup Development Environment**
   - Install dependencies
   - Setup Docker
   - Configure IDE

2. **Create Project Structure**
   - Create all directories
   - Create `__init__.py` files
   - Setup git repo

3. **Start with Phase 1**
   - Implement interfaces
   - Setup configuration
   - Create factories

4. **Incremental Development**
   - One component at a time
   - Test as you go
   - Iterate based on feedback

---

## Questions to Answer During Review

### Architecture Questions

1. **Does the layered architecture make sense?**
   - Presentation → Application → Domain → Infrastructure

2. **Are the interfaces sufficient?**
   - Do they cover all use cases?
   - Are they too generic or too specific?

3. **Is the configuration approach good?**
   - YAML + environment variables
   - Per-environment overrides

4. **Are we following SOLID correctly?**
   - Single Responsibility?
   - Open/Closed?
   - Dependency Inversion?

### Technical Questions

1. **Provider choices:**
   - OpenRouter for LLM - OK?
   - Voyage AI for embeddings - OK?
   - Qdrant for vectors - OK?

2. **Chunking strategies:**
   - Are the 3 strategies enough?
   - Need semantic chunking immediately?

3. **Error handling:**
   - Is the exception hierarchy correct?
   - Retry logic needed?

4. **Performance:**
   - Batch sizes appropriate?
   - Caching strategy?

### Implementation Questions

1. **Testing:**
   - Is 80% coverage target realistic?
   - Unit + Integration + E2E split OK?

2. **Deployment:**
   - Docker Compose for dev - OK?
   - AWS ECS for prod - OK?
   - Need Kubernetes?

3. **Monitoring:**
   - Prometheus metrics - OK?
   - What alerts do we need?

4. **Timeline:**
   - 6 weeks reasonable?
   - Which phases can be parallelized?

---

## Contact & Support

For questions about this implementation guide:
- Review `ARCHITECTURE.md` for detailed design
- Check existing code in `/embed` folder for patterns
- Refer to external provider documentation

---

**Ready to implement? Let's build something great! 🚀**
