import streamlit as st
import requests
import os
import time
from typing import List

# Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_DIR = "uploaded_files"

# Page configuration
st.set_page_config(
    page_title="RAG Knowledge Base with Groq",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'documents_uploaded' not in st.session_state:
        st.session_state.documents_uploaded = False
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = "No documents uploaded"
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def main():
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🔍 RAG Knowledge Base</h1>', unsafe_allow_html=True)
    st.markdown("### Powered by Groq AI • Free & Fast • Your Document Q&A Assistant")
    
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Management")
        st.markdown("---")
        
        uploaded_files = st.file_uploader(
            "Upload PDF or TXT files",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Select one or more PDF or text files to add to your knowledge base"
        )
        
        if uploaded_files:
            st.info(f"📄 {len(uploaded_files)} file(s) selected")
            
            if st.button("🚀 Upload & Process Documents", type="primary"):
                with st.spinner("Processing documents... This may take a few moments."):
                    files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                    
                    try:
                        response = requests.post(f"{API_BASE_URL}/upload", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.documents_uploaded = True
                            st.session_state.processing_status = f"✅ {result['message']}"
                            st.session_state.chunk_count = result['chunks_created']
                            st.success("Documents processed successfully!")
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to the backend server. Make sure it's running on localhost:8000")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
        
        st.markdown("---")
        st.header("ℹ️ System Info")
        
        # System status
        try:
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success(f"🟢 Backend: {health_data.get('status', 'unknown')}")
                st.info(f"🤖 LLM: {health_data.get('llm_provider', 'unknown')}")
            else:
                st.error("🔴 Backend unavailable")
        except:
            st.error("🔴 Cannot connect to backend")
        
        if st.session_state.documents_uploaded:
            try:
                stats_response = requests.get(f"{API_BASE_URL}/stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    st.metric("Documents Processed", stats['documents_processed'])
                    st.metric("Vector Store Size", stats['vector_store_size'])
            except:
                pass
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Ask Questions")
        
        if not st.session_state.documents_uploaded:
            st.warning("⚠️ Please upload documents first using the sidebar to start asking questions.")
            st.info("""
            **How to use:**
            1. 📁 Upload PDF/TXT files using the sidebar
            2. 🚀 Click 'Upload & Process Documents' 
            3. 💬 Start asking questions about your documents
            4. 🔍 Get instant AI-powered answers with citations
            """)
        else:
            # Display processing status
            st.markdown(f'<div class="success-box">{st.session_state.processing_status}</div>', unsafe_allow_html=True)
            
            # Chat interface
            question = st.text_area(
                "Enter your question:",
                placeholder="What would you like to know about your documents?",
                height=100
            )
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col2:
                ask_button = st.button("🤖 Ask Groq AI", type="primary", use_container_width=True)
            with col3:
                clear_button = st.button("🗑️ Clear History", use_container_width=True)
            
            if clear_button:
                st.session_state.chat_history = []
                st.rerun()
            
            if ask_button and question:
                with st.spinner("🔍 Searching documents and generating answer..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/query", 
                            json={"question": question}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": result['answer'],
                                "sources": result['sources'],
                                "timestamp": time.time()
                            })
                        else:
                            st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend server. Make sure it's running.")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
            
            # Display chat history
            st.markdown("---")
            st.subheader("📜 Conversation History")
            
            if not st.session_state.chat_history:
                st.info("No questions asked yet. Enter a question above to start!")
            else:
                for i, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"Q: {chat['question'][:100]}...", expanded=i==0):
                        st.markdown(f"**🤖 Answer:** {chat['answer']}")
                        
                        if chat['sources']:
                            st.markdown("**📚 Sources:**")
                            for source in chat['sources']:
                                with st.expander(f"Source {source['source_id']} (Relevance: {source['similarity_score']})"):
                                    st.text(source['content'])
    
    with col2:
        st.header("⚡ Groq AI Features")
        st.markdown("""
        **🚀 Blazing Fast**
        - Ultra-low latency responses
        - Free tier available
        - No rate limits for testing
        
        **🔍 Smart Search**
        - Semantic document search
        - Relevance-based ranking
        - Multiple source citations
        
        **📚 Document Support**
        - PDF files
        - Text files
        - Batch processing
        
        **🛡️ Privacy Focused**
        - Your data stays local
        - No external storage
        - Secure embeddings
        """)
        
        st.markdown("---")
        st.header("🎯 Sample Questions")
        st.markdown("""
        Try asking:
        - *"Summarize the main points"*
        - *"What are the key findings?"*
        - *"Explain the methodology used"*
        - *"List the recommendations"*
        - *"What problems are addressed?"*
        """)

if __name__ == "__main__":
    main()