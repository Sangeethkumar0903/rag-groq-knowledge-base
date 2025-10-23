import streamlit as st
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Streamlit Page Setup
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon="📚",
    layout="wide",
)

# --- CSS Styling ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        color: #1a237e;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtext {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background-color: #3f51b5;
        color: white;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #303f9f;
        color: white;
        transform: scale(1.02);
    }
    .chat-box {
        background-color: #f8f9fb;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #dcdcdc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .question-text {
        color: #1a237e;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .answer-text {
        background-color: #e8f0fe;
        padding: 0.8rem;
        border-radius: 6px;
        color: #263238;
        line-height: 1.5;
        border: 1px solid #d6e9ff;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if 'documents_uploaded' not in st.session_state:
    st.session_state.documents_uploaded = False
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = "No documents uploaded"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Header ---
st.markdown("<div class='main-title'>📚 RAG Knowledge Base</div>", unsafe_allow_html=True)
st.markdown("<div class='subtext'>Upload your documents and ask anything about them.</div>", unsafe_allow_html=True)

# --- Sidebar: Document Upload ---
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Select PDF or TXT files",
        type=['pdf', 'txt'],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("📤 Upload & Process"):
        with st.spinner("Processing documents..."):
            files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
            try:
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.documents_uploaded = True
                    st.session_state.processing_status = f"✅ {result['message']}"
                    st.success("Documents processed successfully!")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Cannot connect to backend: {str(e)}")

    st.markdown("---")
    st.header("🧠 System Status")

    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            st.success("Backend: Online ✅")
        else:
            st.error("Backend: Offline ❌")
    except:
        st.error("Backend connection failed.")

# --- Main Layout ---
col1, col2 = st.columns([2, 1])

# --- Question Area ---
with col1:
    st.subheader("💬 Ask a Question")

    if not st.session_state.documents_uploaded:
        st.info("Upload documents in the sidebar to start querying your knowledge base.")
    else:
        question = st.text_area("Your Question", placeholder="Ask something about your uploaded documents...")
        colq1, colq2 = st.columns([1, 1])
        with colq1:
            ask_button = st.button("Ask", use_container_width=True)
        with colq2:
            clear_button = st.button("Clear", use_container_width=True)

        if clear_button:
            st.session_state.chat_history = []
            st.rerun()

        if ask_button and question:
            with st.spinner("Generating answer..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/query", json={"question": question})
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": result['answer'],
                            "sources": result['sources'],
                            "timestamp": time.time()
                        })
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")

    st.markdown("---")
    st.subheader("🗂️ Chat History")

    if not st.session_state.chat_history:
        st.info("No questions asked yet.")
    else:
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"""
            <div class='chat-box'>
                <div class='question-text'>❓ {chat['question']}</div>
                <div class='answer-text'>🤖 {chat['answer']}</div>
            </div>
            """, unsafe_allow_html=True)
            if chat['sources']:
                with st.expander("📚 Sources"):
                    for src in chat['sources']:
                        st.text(f"{src['content']}\n")

# --- Example Prompts ---
with col2:
    st.subheader("💡 Example Questions")
    st.markdown("""
    - Summarize the main points  
    - What are the key findings?  
    - Explain the methodology used  
    - List the recommendations  
    - What problems are addressed?  
    """)

