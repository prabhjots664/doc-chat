from microAgents.llm import LLM
from microAgents.core import MicroAgent, Tool, BaseMessageStore
from typing import List, Dict, Any, Optional, Union
from domain.entities import LLMMessage, SearchResult, LLMResponse
from interfaces.llm_provider import ILLMProvider
from interfaces.embedding_provider import IEmbeddingProvider
from interfaces.vector_store import IVectorStore
from core.logging import get_logger

logger = get_logger(__name__)


class DocChatAgent(MicroAgent):
    """Custom agent class for document analysis, adding logging and specific prompting."""
    
    def __init__(self, llm, search_tool: Tool):
        super().__init__(
            llm=llm,
            prompt=(
                "You are an expert Document Analysis Agent.\n"
                "Your goal is to answer questions using ONLY the information you retrieve from 'search_documents'.\n\n"
                "GUIDELINES:\n"
                "1. Always use 'search_documents' first to find relevant information.\n"
                "2. If the documents don't contain the answer, state that you don't know.\n"
                "3. Keep your answers factual and grounded in the retrieved sources.\n"
                "4. GUARDRAIL: If the user uses foul or offensive language, politely decline to answer.\n"
                "5. TOOL USAGE: You have access to 'search_documents'. USE IT. Do not use 'tool_name'."
            ),
            toolsList=[search_tool]
        )
        
    def execute_agent(self, query: str, message_store: BaseMessageStore) -> str:
        """Override execute_agent to add visibility into the agent's thought process."""
        logger.info(f"🤖 [AGENT START] Processing query: '{query}'")
        response = super().execute_agent(query, message_store)
        logger.info(f"🤖 [AGENT END] Final Response: {response[:100]}...")
        return response

class RAGPipelineService:
    """Agentic Service for RAG operations using microAgents."""
    
    def __init__(
        self,
        llm_provider: ILLMProvider,
        embedding_provider: IEmbeddingProvider,
        vector_store: IVectorStore,
        collection_name: str = "documents"
    ):
        self.llm_adapter = llm_provider
        self.embedding = embedding_provider
        self.vector_store = vector_store
        self.collection_name = collection_name
        
        # Initialize LLM directly as per microAgents pattern
        # Extract config from our provider to pass to the library's LLM class
        base_url = getattr(llm_provider, "base_url", "https://openrouter.ai/api/v1")
        api_key = getattr(llm_provider, "api_key", "")
        model = getattr(llm_provider, "model")  # No fallback - must come from config/env
        
        self.micro_llm = LLM(
            base_url=base_url,
            api_key=api_key,
            model=model,
            max_tokens=4000,
            temperature=0.1
        )
        logger.info(f"🤖 [RAG INIT] Using LLM model: {model}")
        
        # Tool definition
        def search_documents(query: str) -> str:
            """Searches for relevant context in the document collection."""
            return self._execute_search(query)

        self.search_tool = Tool(
            description="Search the document collection. Input: query (str)",
            func=search_documents
        )
        
        # Initialize our custom agent (Inheritance Pattern)
        self.agent = DocChatAgent(
            llm=self.micro_llm,
            search_tool=self.search_tool
        )

        # WORKAROUND: microAgents library uses '<tool_name>' in its prompt examples (line 33 of prompt.py)
        # Some models copy this literally instead of using 'search_documents'
        # This trap intercepts the hallucination and executes the correct tool automatically
        def tool_name(query: str = "", **kwargs) -> str:
            """Catches library prompt hallucination and redirects to actual search."""
            logger.warning(f"⚠️ [HALLUCINATION TRAP] Model used 'tool_name' instead of 'search_documents'. Auto-fixing...")
            # Execute the correct tool directly instead of asking LLM to retry
            return self._execute_search(query if query else kwargs.get('param1', ''))

        self.hallucination_trap = Tool(
            description="Internal fallback for prompt confusion",
            func=tool_name
        )
        self.agent.register_tool(self.hallucination_trap)
        
        self._last_search_results = []
        logger.info(f"Initialized Agentic RAGPipelineService with Adapter: collection={collection_name}")
    
    def _execute_search(self, query: str) -> str:
        try:
            logger.info(f"🔍 [RAG FLOW] Agent executing search: '{query}'")
            embedding_result = self.embedding.embed([query], input_type="query")
            query_vector = embedding_result.embeddings[0]
            search_results = self.vector_store.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=5
            )
            self._last_search_results.extend(search_results)
            
            if not search_results:
                logger.warning(f"⚠️ [RAG FLOW] No results found for query: '{query}'")
                return "No relevant information found for this query."
            
            # Log retrieved chunks for debugging
            logger.info(f"📚 [RAG FLOW] Retrieved {len(search_results)} chunks")
            for i, res in enumerate(search_results):
                preview = res.text[:100].replace('\n', ' ') + "..."
                logger.info(f"   Shape {i+1}: {preview} (Score: {res.score:.4f})")
            
            return "\n\n".join([f"Source {i+1}:\n{res.text}" for i, res in enumerate(search_results)])
        except Exception as e:
            logger.error(f"❌ [RAG FLOW] Error in search: {str(e)}")
            return f"Error performing search: {str(e)}"

    def query(
        self,
        user_query: str,
        limit: int = 5,
        chat_history: Optional[List[LLMMessage]] = None
    ) -> LLMResponse:
        try:
            logger.info(f"🚀 [RAG FLOW] Starting new query: '{user_query}'")
            self._last_search_results = [] 
            message_store = BaseMessageStore()
            if chat_history:
                for msg in chat_history:
                    message_store.add_message({'role': msg.role, 'content': msg.content})
            
            agent_response = self.agent.execute_agent(user_query, message_store)
            
            logger.info(f"✅ [RAG FLOW] Final Answer: {agent_response[:200]}...")
            
            return LLMResponse(
                content=agent_response,
                model=self.micro_llm.model,
                tokens_used=0,
                finish_reason="stop",
                metadata={"agentic": True, "search_results_count": len(self._last_search_results)}
            )
        except Exception as e:
            logger.error(f"Error in Agentic RAG query execution: {str(e)}")
            raise
