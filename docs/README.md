# Document Chat System - RAG Application

> A production-grade Retrieval-Augmented Generation (RAG) system for conversational AI over document collections, built with clean architecture and SOLID principles.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%2B%20SOLID-green.svg)](./ARCHITECTURE.md)
[![Status](https://img.shields.io/badge/Status-Design%20Phase-yellow.svg)]()

---

## 🎯 Overview

This system enables users to:
- **Upload documents** in multiple formats (PDF, DOCX, TXT, MD, etc.)
- **Ask questions** about the uploaded content
- **Get accurate answers** grounded in the documents with source citations
- **Have conversations** with context awareness

### Key Features

✨ **Multi-Format Support** - PDF, DOCX, TXT, MD, RTF, ODT  
🧠 **Intelligent Chunking** - Multiple strategies (by title, paragraph, sentence)  
🔍 **Semantic Search** - Vector-based similarity search with Qdrant  
💬 **Conversational AI** - Powered by OpenRouter (Claude, GPT-4, etc.)  
🎨 **Modern UI** - Built with Streamlit  
🏗️ **Clean Architecture** - SOLID principles, design patterns  
🔧 **Configurable** - YAML-based configuration system  
🐳 **Containerized** - Docker & Docker Compose ready  
📊 **Observable** - Structured logging and metrics  

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | **Complete architecture documentation** - Design principles, components, interfaces, data flow, deployment strategy |
| [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) | **Developer guide** - Implementation phases, code examples, best practices, debugging tips |
| [assignment.md](./assignment.md) | **Original assignment** - Requirements and expectations |

---

## 🏗️ Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                  (Streamlit UI / REST API)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ChatService → RAGPipeline → DocumentProcessing    │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ILLMProvider  │  │IEmbedding    │  │IVectorStore  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │OpenRouter    │  │VoyageAI      │  │Qdrant        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

- **SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Design Patterns** - Strategy, Adapter, Factory, Dependency Injection, Repository
- **Clean Architecture** - Clear separation of concerns, dependency inversion
- **Configuration-Driven** - All settings in YAML, easy to change providers

---

## 🚀 Quick Start (Coming Soon)

> **Note**: Currently in design phase. Implementation will begin after architecture review.

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenRouter API key
- Voyage AI API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd doc-chat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys

# Start Qdrant (vector database)
docker-compose up -d qdrant

# Run application
streamlit run app.py
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

---

## 💻 Technology Stack

### Core Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.10+ | Rich ecosystem, async support |
| **LLM Provider** | OpenRouter | Multi-model access, cost-effective |
| **Embeddings** | Voyage AI | High quality, competitive pricing |
| **Vector Database** | Qdrant | Production-ready, filtering support |
| **Document Processing** | Unstructured | Multi-format support |
| **Web Framework** | Streamlit | Rapid prototyping, interactive UI |
| **Configuration** | YAML + Pydantic | Type-safe, environment overrides |

### Why These Choices?

#### OpenRouter for LLM
- **Multi-Model Access**: Claude, GPT-4, Llama, Mistral, etc.
- **Cost-Effective**: Competitive pricing, no vendor lock-in
- **OpenAI-Compatible API**: Easy to swap providers
- **Unified Interface**: One API for multiple models

#### Voyage AI for Embeddings
- **High Quality**: State-of-the-art embedding models
- **Domain-Specific**: Optimized for document retrieval
- **Good Pricing**: Competitive vs. OpenAI
- **Separate Query/Document Types**: Better retrieval quality

#### Qdrant for Vector Storage
- **Production-Ready**: Battle-tested in production
- **Rich Filtering**: Metadata filtering capabilities
- **Fast**: Sub-100ms search times
- **Easy Deployment**: Docker container available
- **Horizontal Scaling**: Distributed mode available

---

## 🎨 Project Structure

```
doc-chat/
├── config/                    # Configuration files
│   ├── config.yaml           # Base configuration
│   ├── development.yaml      # Dev overrides
│   └── production.yaml       # Production config
│
├── core/                      # Core utilities
│   ├── config.py             # Configuration loader
│   ├── logging.py            # Logging setup
│   └── exceptions.py         # Custom exceptions
│
├── interfaces/                # Interface contracts (ABC)
│   ├── llm_provider.py       # LLM interface
│   ├── embedding_provider.py # Embedding interface
│   ├── vector_store.py       # Vector DB interface
│   ├── document_loader.py    # Document loader interface
│   └── document_chunker.py   # Chunking interface
│
├── providers/                 # Provider implementations
│   ├── openrouter_llm.py     # OpenRouter adapter
│   ├── voyageai_embedding.py # Voyage AI adapter
│   ├── qdrant_adapter.py     # Qdrant adapter
│   └── unstructured_loader.py# Document loader
│
├── services/                  # Application services
│   ├── chat_service.py       # Main chat orchestrator
│   ├── document_processing_service.py
│   ├── rag_pipeline_service.py
│   └── guardrails_manager.py
│
├── factories/                 # Factory classes
│   ├── provider_factory.py   # Create providers
│   └── service_factory.py    # Create services
│
├── domain/                    # Domain entities
│   └── entities.py           # Document, Chunk, etc.
│
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
│
├── app.py                     # Streamlit UI entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-container setup
└── .env.example              # Example environment vars
```

---

## 🔧 Configuration

### Configuration Files

The system uses a hierarchical configuration system:

1. **Base Config** (`config/config.yaml`) - Default settings
2. **Environment Config** (`config/development.yaml`) - Environment-specific overrides
3. **Environment Variables** (`.env`) - Secrets and local overrides

### Example Configuration

```yaml
# config/config.yaml
llm:
  provider: "openrouter"
  model: "anthropic/claude-3-sonnet"
  parameters:
    temperature: 0.7
    max_tokens: 4000

embeddings:
  provider: "voyageai"
  model: "voyage-2"
  dimension: 1024

vector_db:
  provider: "qdrant"
  host: "localhost"
  port: 6333
  collection_name: "documents"
```

### Environment Variables

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-xxx
VOYAGEAI_API_KEY=pa-xxx
APP_ENV=development
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Unit tests (60%)
│   ├── test_chunker.py
│   ├── test_embedding.py
│   └── test_providers.py
├── integration/       # Integration tests (30%)
│   └── test_document_processing.py
└── e2e/              # End-to-end tests (10%)
    └── test_chat_flow.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_chunker.py -v

# Run only failed tests
pytest --lf
```

### Coverage Goals

- **Overall**: 85%
- **Providers**: 90%
- **Services**: 85%
- **Domain Logic**: 90%

---

## 📊 Monitoring & Observability

### Structured Logging

```python
logger.info(
    "document_processed",
    document_id=doc_id,
    chunks_created=25,
    processing_time_ms=1234,
    file_type=".pdf"
)
```

### Metrics

- **Query Latency**: P50, P95, P99 response times
- **Embedding Latency**: Time to generate embeddings
- **Vector Search Latency**: Time for similarity search
- **Token Usage**: LLM and embedding token consumption
- **Error Rates**: Errors by component and type

### Health Checks

```bash
# Check system health
curl http://localhost:8501/health

# Response:
{
  "status": "healthy",
  "checks": {
    "qdrant": "healthy",
    "openrouter": "healthy",
    "voyageai": "healthy"
  }
}
```

---

## 🔐 Security

### API Key Management

- ✅ All API keys in environment variables
- ✅ Never committed to repository
- ✅ Use AWS Secrets Manager in production
- ✅ Regular key rotation

### Input Validation

- ✅ File size limits (50 MB default)
- ✅ Supported file types whitelist
- ✅ Query length limits
- ✅ SQL injection prevention

### Output Sanitization

- ✅ PII detection and removal
- ✅ Sensitive pattern filtering
- ✅ Response length limits

---

## 📈 Performance

### Optimization Strategies

1. **Batch Processing**: Process multiple documents in parallel
2. **Connection Pooling**: Reuse database connections
3. **Caching**: Cache embeddings for common queries
4. **Async Operations**: Use async I/O for external APIs

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Query Response Time | < 3s (p95) | Including retrieval + generation |
| Document Upload | < 30s | For 10 MB document |
| Vector Search | < 500ms | For top-5 retrieval |
| Concurrent Users | 100 | With auto-scaling |

---

## 🚢 Deployment

### Local Development

```bash
# Start Qdrant
docker-compose up -d qdrant

# Run application
streamlit run app.py
```

### Docker Compose (Production-like)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### AWS Deployment (Future)

- **ECS Fargate**: Serverless containers for app
- **ECS Service**: Dedicated Qdrant instance with EBS
- **ALB**: Load balancing with SSL termination
- **S3**: Document storage
- **CloudWatch**: Centralized logging
- **Secrets Manager**: API key management

---

## 🎯 Roadmap

### ✅ Phase 1: Foundation (Current)
- [x] Architecture design
- [x] Interface definitions
- [x] Technology selection
- [ ] Implementation begins

### 🚧 Phase 2: Core Implementation (Week 1-4)
- [ ] Provider implementations
- [ ] Document processing pipeline
- [ ] RAG pipeline
- [ ] Chat service

### 📋 Phase 3: UI & Polish (Week 5-6)
- [ ] Streamlit interface
- [ ] File upload functionality
- [ ] Chat interface
- [ ] Settings panel

### 🔮 Future Enhancements
- [ ] Multi-tenancy support
- [ ] Advanced search (hybrid)
- [ ] Re-ranking
- [ ] REST API
- [ ] Authentication
- [ ] Multi-modal support (images, tables)
- [ ] Real-time document updates

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD)
3. Implement feature
4. Run tests: `pytest`
5. Run linters: `black . && flake8 . && mypy .`
6. Commit: `git commit -m "feat: your feature"`
7. Push and create PR

### Code Review Checklist

- [ ] Follows SOLID principles
- [ ] Has unit tests (>80% coverage)
- [ ] Has integration tests (if applicable)
- [ ] Type hints on all functions
- [ ] Docstrings on public methods
- [ ] Error handling present
- [ ] Logging added
- [ ] Configuration-driven (no hardcoded values)

---

## 📝 Technical Decisions

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Interfaces over Implementations** | Enable swapping providers, facilitate testing, support parallel development |
| **Dependency Injection** | Improve testability, reduce coupling, make dependencies explicit |
| **Factory Pattern** | Centralize object creation, enable configuration-based setup |
| **Strategy Pattern for Chunking** | Support multiple chunking algorithms, easy to add new strategies |
| **Configuration-Driven** | Change behavior without code changes, environment-specific configs |
| **Structured Logging** | Machine-parseable logs, better debugging, metrics integration |

### Trade-offs

| Choice | Pros | Cons | Decision |
|--------|------|------|----------|
| OpenRouter vs Direct Provider | Multi-model, cost-effective | Extra hop, dependency | ✅ Use OpenRouter |
| Voyage AI vs Local Embeddings | Higher quality, faster | API costs, dependency | ✅ Use Voyage AI (with local fallback) |
| Qdrant vs FAISS | Production-ready, filtering | External dependency | ✅ Use Qdrant |
| Streamlit vs FastAPI | Rapid dev, interactive | Limited customization | ✅ Use Streamlit (API later) |

---

## 📖 Resources

### External Documentation

- [OpenRouter API Docs](https://openrouter.ai/docs)
- [Voyage AI Documentation](https://docs.voyageai.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Unstructured.io Docs](https://unstructured-io.github.io/unstructured/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Learning Resources

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Design Patterns - Gang of Four](https://refactoring.guru/design-patterns)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

## 🐛 Troubleshooting

### Common Issues

#### Qdrant Connection Failed

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Start Qdrant
docker-compose up -d qdrant

# Check logs
docker logs qdrant
```

#### API Key Not Found

```bash
# Check .env file exists
ls -la .env

# Verify API keys are set
grep OPENROUTER_API_KEY .env
grep VOYAGEAI_API_KEY .env
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

---

## 📧 Support

For questions or issues:
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for design details
- Check [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for dev guidance
- Review existing code in `/embed` folder for patterns

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenRouter** - Multi-model LLM access
- **Voyage AI** - High-quality embeddings
- **Qdrant** - Vector database
- **Unstructured** - Document processing
- **Streamlit** - Web framework

---

**Built with ❤️ using Clean Architecture and SOLID Principles**

