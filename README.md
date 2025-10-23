Knowledge-Base Search Engine — RAG with Groq AI
Short Description

A complete Retrieval-Augmented Generation (RAG) system that ingests PDFs and text documents and provides AI-powered answers using semantic search and Groq's fast LLM inference.

Features

PDF and text document processing

Semantic search with FAISS vector store

Groq AI integration (Llama-3.1-8B)

Streamlit web interface

Fast, free LLM responses

Local embedding generation

Getting Started
1️⃣ Clone the repository
git clone https://github.com/Sangeethkumar0903/rag-groq-knowledge-base.git
cd rag-groq-knowledge-base

2️⃣ Set up Python virtual environment
python -m venv groq_rag_env
groq_rag_env\Scripts\activate      # Windows
# source groq_rag_env/bin/activate  # Linux/macOS

3️⃣ Install dependencies
cd backend
pip install -r requirements.txt

4️⃣ Configure environment variables

Add your GROQ_API_KEY to a .env file in the project root.

5️⃣ Run the backend
cd backend
python main.py

6️⃣ Run the frontend (in a new terminal)
cd frontend
streamlit run app.py

Usage

Upload PDFs or text documents through the web interface.

Ask questions about your documents.

Get AI-generated answers with source citations.

Architecture

Document Processing: PyMuPDF for PDFs, text splitting into chunks

Embeddings: Sentence-transformers for local embedding generation

Vector Store: FAISS for efficient similarity search

Retrieval: Semantic search with cosine similarity

Synthesis: Groq AI with RAG prompt engineering

API: FastAPI backend with REST endpoints

Frontend: Streamlit user interface

API Endpoints

POST /upload – Upload and process documents

POST /query – Query the knowledge base

GET /health – System health check

GET /stats – System statistics
