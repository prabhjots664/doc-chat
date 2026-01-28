# 🤖 Doc-Chat Agent: Production-Grade RAG System

> **Assignment - Option 1: Chat With Your Docs**
> A professional-grade Retrieval-Augmented Generation (RAG) system for conversational AI over document collections, built with Clean Architecture, SOLID principles, and a premium Streamlit interface.

---

### ⚡ Zero-Config Evaluation
For the convenience of the review team, this repository is **pre-configured** with demo API keys. You can skip manual configuration and launch immediately to test the full agentic search and RAG capabilities.

1.  **Launch**:
    ```bash
    docker-compose up -d
    ```
2.  **Access**: Visit **[http://localhost:8501](http://localhost:8501)**

---

## 🚀 (a) Quick Setup Instructions (Manual)

If you prefer to use your own keys:

1.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # 💡 Add your OPENROUTER_API_KEY and VOYAGEAI_API_KEY to .env
    ```
2.  **Launch with Docker**:
    ```bash
    docker-compose up -d
    ```
3.  **Stop**:
    ```bash
    docker-compose down
    ```

### Manual Installation (Development)
1.  **Virtual Env**: `python -m venv .venv && source .venv/bin/activate`
2.  **Dependencies**: `pip install -r requirements.txt`
3.  **Run Qdrant**: `docker run -p 6333:6333 qdrant/qdrant`
4.  **Run App**: `streamlit run app.py`

---

## 🏗️ (b) Architecture Overview

The system follows **Clean Architecture** patterns to ensure that business logic remains decoupled from external infrastructure.

### Layered Architecture Design
```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                               │
│                                                                       │
│  ┌────────────────────┐              ┌────────────────────┐         │
│  │  Streamlit UI      │              │   REST API         │         │
│  │  - File Upload     │              │   (Future)         │         │
│  │  - Chat Interface  │              │   - /chat          │         │
│  │  - Settings        │              │   - /upload        │         │
│  └────────────────────┘              └────────────────────┘         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                                │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              ChatService (Main Orchestrator)                  │  │
│  │  Dependencies:                                                │  │
│  │    - ILLMProvider                                             │  │
│  │    - IEmbeddingProvider                                       │  │
│  │    - IVectorStore                                             │  │
│  │    - GuardrailsManager                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐ │
│  │DocumentProcessing  │  │  RAGPipeline       │  │ Guardrails   │ │
│  │Service             │  │  Service           │  │ Manager      │ │
│  └────────────────────┘  └────────────────────┘  └──────────────┘ │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (Business Logic)                     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    INTERFACES (Contracts)                     │   │
│  ├───────────────────┬───────────────────┬──────────────────────┤   │
│  │ ILLMProvider      │IEmbeddingProvider │ IVectorStore         │   │
│  │ IDocumentLoader   │IDocumentChunker   │ IMetadataExtractor   │   │
│  └───────────────────┴───────────────────┴──────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 IMPLEMENTATIONS (Strategies)                  │   │
│  ├───────────────────────────────────────────────────────────────┤   │
│  │ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │   │
│  │ │OpenRouter       │  │VoyageAI         │  │Qdrant        │  │   │
│  │ │Adapter          │  │Adapter          │  │Adapter       │  │   │
│  │ └─────────────────┘  └─────────────────┘  └──────────────┘  │   │
│  │                                                               │   │
│  │ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │   │
│  │ │Unstructured     │  │Semantic         │  │Local         │  │   │
│  │ │Loader           │  │Chunker          │  │Embedding     │  │   │
│  │ └─────────────────┘  └─────────────────┘  └──────────────┘  │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     DOMAIN ENTITIES                           │   │
│  ├───────────────────────────────────────────────────────────────┤   │
│  │ Document, Chunk, SearchResult, ChatMessage, EmbeddingResult   │   │
│  └───────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │
│  │  Qdrant     │  │ OpenRouter  │  │ Voyage AI   │  │ File     │  │
│  │  (Docker)   │  │   (API)     │  │   (API)     │  │ System   │  │
│  │  Port: 6333 │  │             │  │             │  │          │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │  Logging    │  │ Monitoring  │  │ Config      │                │
│  │  (JSON)     │  │ (Metrics)   │  │ (YAML)      │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow
```
┌──────┐                                                     ┌──────────┐
│ User │                                                     │OpenRouter│
└───┬──┘                                                     └────┬─────┘
    │                                                             │
    │ 1. Upload Document                                          │
    │─────────────────────────►┌────────────────┐                │
    │                          │ ChatService    │                │
    │                          └───────┬────────┘                │
    │                                  │                          │
    │                                  │ 2. Process Document      │
    │                                  ▼                          │
    │                          ┌────────────────┐                │
    │                          │DocumentProcess │                │
    │                          │ingService      │                │
    │                          └───────┬────────┘                │
    │                                  │                          │
    │         ┌────────────────────────┼────────────┐            │
    │         │                        │            │            │
    │         │ 3. Load      4. Chunk  │  5. Embed  │            │
    │         ▼                        ▼            ▼            │
    │  ┌──────────┐         ┌─────────────┐  ┌──────────┐      │
    │  │Unstructd │         │Semantic     │  │VoyageAI  │      │
    │  │Loader    │         │Chunker      │  │Adapter   │      │
    │  └──────────┘         └─────────────┘  └────┬─────┘      │
    │                                              │            │
    │                                              │ 6. Generate│
    │                                              │ Embeddings │
    │                                              ▼            │
    │                                     ┌────────────────┐   │
    │                                     │  Voyage AI API │   │
    │                                     └────────┬───────┘   │
    │                                              │            │
    │                                              │ 7. Store   │
    │                                              ▼            │
    │                                     ┌────────────────┐   │
    │                                     │  Qdrant DB     │   │
    │                                     └────────────────┘   │
    │                                                           │
    │ 8. Chat Query                                            │
    │─────────────────────────►┌────────────────┐             │
    │                          │ RAGPipeline    │             │
    │                          └───────┬────────┘             │
    │                                  │                       │
    │                  ┌───────────────┼───────────────┐      │
    │                  │               │               │      │
    │         9. Embed Query  10. Search    11. Generate      │
    │                  ▼               ▼               │      │
    │           ┌──────────┐   ┌──────────┐           │      │
    │           │VoyageAI  │   │ Qdrant   │           │      │
    │           └──────────┘   └──────────┘           │      │
    │                                                  │      │
    │                                        12. LLM Call      │
    │                                                  ▼      │
    │                                          ┌──────────┐   │
    │                                          │OpenRouter│───┘
    │                                          └────┬─────┘
    │                                               │
    │ 13. Response                                  │
    │◄──────────────────────────────────────────────┘
    │
```

---

## 🧠 (d) RAG/LLM Approach & Decisions

### Technical Choices & Alternatives Considered
| Component | Choice | Alternatives Considered | Decision Rationale |
| :--- | :--- | :--- | :--- |
| **LLM** | **GLM-4.5** (via OpenRouter) | GPT-4o, Claude 3.5 Sonnet | Exceptional reasoning scores vs. cost; highly stable for multi-step agentic search. |
| **Embeddings**| **Voyage AI (voyage-context-3)** | OpenAI text-embedding-3, BGE | Optimized specifically for retrieval-heavy contexts; superior long-context performance. |
| **Vector DB** | **Qdrant** | FAISS, Pinecone, Weaviate | Native support for modern `query_points` API; robust metadata filtering and container ease. |
| **Orchestration**| **microAgents** (Custom) | LangChain, LlamaIndex | **Built by the author.** demonstrates deeper agentic understanding than using a wrapper library. |

### Context Management & Ingestion
- **Chunking Strategy**: Paragraph-based (by_paragraph) with 50-token overlap to maintain semantic continuity.
- **Prompting**: Using a structured system prompt that enforces document grounding and multi-step reasoning.
- **Guardrails**: Implementation of a `GuardrailsManager` that validates retrieval scores and filters responses for hallucination risk.

---

## 🛠️ (e) Key Technical Decisions

1.  **Interfaces over Implementations (DIP)**: No service depends on a concrete class like `QdrantClient`. Instead, they depend on internal interfaces. This allows switching providers in minutes.
2.  **Direct Custom Orchestration**: I chose to use my own framework, **microAgents**, rather than LangChain. This was a deliberate choice to demonstrate engineering from first principles and keep the dependency graph clean and observable.
3.  **Agentic Search**: Instead of a "dumb" retrieve-then-read flow, the system uses an agent that can decide if it needs to perform follow-up searches to answer complex, multi-part questions.

---

## 📐 (f) Engineering Standards

- **SOLID Principles**: Strictly followed to ensure maintainability (e.g., SRP for Document loaders vs. Chunkers).
- **Type Hinting**: 100% coverage of Python type hints for static analysis and self-documenting code.
- **Testing Pyramid**: Standardized on Integration tests (`test_chat_flow.py`) for the core RAG pipeline, supplemented by unit tests for logic-heavy components like chunking.
- **Structured Logging**: Using the `logging` module to provide a JSON-compatible trace of the agent's thought process.

---

## 🤖 (g) AI Tool Usage Philosophy

During development, AI coding assistants were used as **high-bandwidth pair programmers**.

- **Boilerplate**: AI generated the initial skeleton for repetitive adapter classes.
- **UI/CSS**: AI refined the premium Streamlit glassmorphism styling.
- **Authorship vs. Output**: While AI helped write code, the **architecture was human-designed**. I authored the `microAgents` framework myself to ensure the core logic follows my preferred engineering rigor rather than accepting LLM-generated "spaghetti" logic.

---

## 🚢 (c) Productionization & Scalability

To deploy this system to a hyper-scaler (AWS/GCP/Azure):

### Cloud Deployment Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    VPC (10.0.0.0/16)                      │  │
│  │                                                             │  │
│  │  ┌───────────────────────────────────────────────────┐   │  │
│  │  │         Public Subnet (10.0.1.0/24)                │   │  │
│  │  │                                                     │   │  │
│  │  │  ┌──────────────────────┐                          │   │  │
│  │  │  │ Application Load     │                          │   │  │
│  │  │  │ Balancer (ALB)       │                          │   │  │
│  │  │  │ - SSL/TLS            │                          │   │  │
│  │  │  │ - WAF                │                          │   │  │
│  │  │  └──────┬───────────────┘                          │   │  │
│  │  └─────────┼──────────────────────────────────────────┘   │  │
│  │            │                                               │  │
│  │  ┌─────────▼────────────────────────────────────────┐    │  │
│  │  │      Private Subnet (10.0.2.0/24)                 │    │  │
│  │  │                                                     │    │  │
│  │  │  ┌────────────────────────────────────────┐       │    │  │
│  │  │  │  ECS Fargate Service                   │       │    │  │
│  │  │  │  ┌──────────┐  ┌──────────┐            │       │    │  │
│  │  │  │  │  Task 1  │  │  Task 2  │  (Auto     │       │    │  │
│  │  │  │  │ (App)    │  │ (App)    │   Scaling) │       │    │  │
│  │  │  │  └──────────┘  └──────────┘            │       │    │  │
│  │  │  └────────────────────────────────────────┘       │    │  │
│  │  │                                                     │    │  │
│  │  │  ┌────────────────────────────────────────┐       │    │  │
│  │  │  │  Qdrant (ECS Service)                  │       │    │  │
│  │  │  │  - Persistent volume (EBS)             │       │    │  │
│  │  │  │  - Port 6333                           │       │    │  │
│  │  │  └────────────────────────────────────────┘       │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   S3 Bucket  │  │  CloudWatch  │  │  Secrets     │          │
│  │  (Documents) │  │  (Logs)      │  │  Manager     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

1.  **Managed Orchestration**: Run the app on **ECS Fargate** (AWS) or **GKE** (GCP) for auto-scaling.
2.  **State Management**: Move from local `uploads/` to **S3** or **GCS** with signed URLs for secure access.
3.  **Async Processing**: Replace synchronous ingestion with an **Asynchronous Task Queue** (Celery + Redis) to handle large document imports without blocking the UI.
4.  **Observability Stack**: Integrate **Arize Phoenix** or **LangSmith** for specialized RAG tracing and hallucination monitoring.
5.  **Global Vector DB**: Use **Qdrant Cloud** or a managed cluster with horizontal sharding for high-availability.

---

## 🔮 (h) What I'd Do Differently With More Time

1.  **Semantic Chunking**: Instead of paragraph breaks, use embedding clusters to determine where one topic ends and another begins.
2.  **Hybrid Search**: Add Sparse search (BM25) alongside Dense (Embeddings) to improve retrieval on specific keywords and serial numbers.
3.  **Multi-user Isolation**: Implement multi-tenant collections in Qdrant so different users can have isolated document spaces.

---

## (i) Final Note
This project represents a balance between rapid execution and strict engineering discipline. Every line of code was reviewed for architectural integrity, ensuring that this RAG agent isn't just a demo, but a foundation for a scalable product.

**Built with ❤️ for Lead Gen AI Engineer Assignment**
