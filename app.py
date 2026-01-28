import streamlit as st
import os
import tempfile
from pathlib import Path
import time
import base64

from factories.service_factory import ServiceFactory
from domain.entities import ChatMessage
from core.logging import get_logger

# Configure logging
logger = get_logger(__name__)

# --- UTILS & CONSTANTS ---
PAGE_TITLE = "Doc-Chat Agent"
PAGE_ICON = "🤖"

# --- CUSTOM CSS FOR PREMIUM LOOK ---
def local_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        
        /* Glassmorphism Sidebar */
        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        /* Chat Message Styling */
        .stChatMessage {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .stChatMessage.user {{
            background: linear-gradient(135deg, rgba(100, 100, 255, 0.1), rgba(150, 150, 255, 0.1));
            border: 1px solid rgba(100, 100, 255, 0.2);
        }}
        
        /* Thinking Indicator */
        .thinking {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-style: italic;
            color: #888;
            margin-bottom: 10px;
        }}
        
        .thinking-dot {{
            width: 8px;
            height: 8px;
            background-color: #555;
            border-radius: 50%;
            display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
        }}
        
        .thinking-dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .thinking-dot:nth-child(2) {{ animation-delay: -0.16s; }}
        
        @keyframes bounce {{
            0%, 80%, 100% {{ transform: scale(0); }}
            40% {{ transform: scale(1.0); }}
        }}
        
        /* Premium Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #5c7dfa, #9666d2);
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin-right: 5px;
        }}
        .status-healthy {{ background-color: rgba(0, 255, 0, 0.1); color: #00ff00; border: 1px solid rgba(0, 255, 0, 0.2); }}
        .status-degraded {{ background-color: rgba(255, 0, 0, 0.1); color: #ff0000; border: 1px solid rgba(255, 0, 0, 0.2); }}
        
        </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---

def initialize_app():
    """Set up the page and session state."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide"
    )
    local_css()
    
    if 'chat_service' not in st.session_state:
        try:
            with st.spinner("🚀 Initializing doc-chat services..."):
                st.session_state.chat_service = ServiceFactory.create_chat_service()
                st.session_state.session_id = f"session_{int(time.time())}"
                st.session_state.messages = []
                st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize services: {str(e)}")
            st.session_state.initialized = False

def sidebar_content():
    """Render sidebar elements."""
    with st.sidebar:
        st.title(f"{PAGE_ICON} {PAGE_TITLE}")
        
        # System status
        if st.session_state.get('initialized'):
            try:
                status = st.session_state.chat_service.get_system_status()
                if status['status'] == 'healthy':
                    st.markdown('<div class="status-badge status-healthy">● System Healthy</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge status-degraded">● System Degraded</div>', unsafe_allow_html=True)
                
                st.caption(f"LLM: {status.get('llm_model')}")
                st.caption(f"Vector Store: Qdrant")
                
                col_info = status.get('vector_db', {})
                st.info(f"📚 Documents: {col_info.get('vectors_count', 0)} chunks")
            except Exception as e:
                st.error("Could not fetch status")
        
        st.divider()
        
        # File management
        st.subheader("📄 Document Management")
        uploaded_files = st.file_uploader(
            "Upload documents (PDF, MD, TXT, DOCX)",
            accept_multiple_files=True,
            type=['pdf', 'md', 'txt', 'docx']
        )
        
        if st.button("Ingest Documents") and uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Ingesting {uploaded_file.name}..."):
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Process
                    success = st.session_state.chat_service.ingest_document(tmp_path)
                    
                    # Cleanup
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
                    
                    if success:
                        st.success(f"Ingested {uploaded_file.name}")
                    else:
                        st.error(f"Failed to ingest {uploaded_file.name}")
            st.rerun()

        st.divider()
        
        # Chat Controls
        st.subheader("⚙️ Chat Controls")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_service.clear_session(st.session_state.session_id)
            st.session_state.messages = []
            st.success("History cleared!")
            time.sleep(1)
            st.rerun()
            
        st.toggle("Use RAG (Document context)", value=True, key="use_rag")

def chat_interface():
    """Render the main chat interface."""
    st.subheader("💬 Conversations")
    
    # Display message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("metadata") and "search_queries" in message["metadata"]:
                with st.expander("🔍 Search details"):
                    st.write(message["metadata"]["search_queries"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            # Mock thinking steps for visual feedback
            # In a real app, this would be hooked into the agent's actual steps
            status_container = st.empty()
            with status_container.container():
                st.markdown("""
                    <div class="thinking">
                        <span class="thinking-dot"></span>
                        <span class="thinking-dot"></span>
                        <span class="thinking-dot"></span>
                        <span>Agent is thinking and searching documents...</span>
                    </div>
                """, unsafe_allow_html=True)
            
            try:
                # Call the service
                response: ChatMessage = st.session_state.chat_service.chat(
                    session_id=st.session_state.session_id,
                    user_message=prompt,
                    use_rag=st.session_state.use_rag
                )
                
                # Clear thinking indicator and show final response
                status_container.empty()
                st.markdown(response.content)
                
                # Add to state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "metadata": response.metadata
                })
                
            except Exception as e:
                status_container.error(f"An error occurred: {str(e)}")

def main():
    initialize_app()
    if not st.session_state.get('initialized'):
        st.warning("⚠️ Application not fully initialized. Please check backend logs.")
        return
        
    sidebar_content()
    chat_interface()

if __name__ == "__main__":
    main()
