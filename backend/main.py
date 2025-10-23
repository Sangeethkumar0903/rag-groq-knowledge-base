from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import List
import uvicorn
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = FastAPI(
    title="RAG Knowledge Base with Groq",
    description="Working RAG system with Groq AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple storage
documents_store = []
UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SimpleGroqIntegration:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
    
    def create_rag_prompt(self, context_chunks: List[str], query: str) -> str:
        """Create RAG prompt with context and query"""
        context_text = "\n\n".join([f"Source {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are a helpful AI assistant. Using ONLY the context provided below from uploaded documents, answer the user's question accurately and concisely.

IMPORTANT RULES:
1. Answer based STRICTLY on the provided context only
2. Be accurate and concise
3. If the context doesn't contain enough information, say "The documents do not contain enough information to answer this question."
4. Never make up information

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        """Generate answer using Groq API"""
        if not self.api_key:
            return "❌ Error: GROQ_API_KEY not found"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that provides accurate answers based only on the given context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1024
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"

llm_integration = SimpleGroqIntegration()

def extract_text_from_file(file_path: str) -> str:
    """Extract text from file with better error handling"""
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if content.strip():
                    return content
                else:
                    return f"Empty text file: {os.path.basename(file_path)}"
                    
        elif file_path.endswith('.pdf'):
            try:
                import fitz
                doc = fitz.open(file_path)
                text = ""
                for page_num, page in enumerate(doc):
                    page_text = page.get_text()
                    if page_text.strip():
                        text += f"Page {page_num + 1}:\n{page_text}\n\n"
                doc.close()
                
                if text.strip():
                    return text
                else:
                    return f"PDF file contains no extractable text: {os.path.basename(file_path)}"
                    
            except ImportError:
                return f"PDF file: {os.path.basename(file_path)} (install pymupdf for text extraction)"
            except Exception as e:
                return f"Error reading PDF {os.path.basename(file_path)}: {str(e)}"
                
        else:
            return f"Unsupported file type: {os.path.basename(file_path)}"
            
    except Exception as e:
        return f"Error reading file {os.path.basename(file_path)}: {str(e)}"
def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def simple_retrieve(query: str, chunks: List[str], k: int = 3) -> List[tuple]:
    """Simple keyword-based retrieval with proper scoring"""
    query_words = set(query.lower().split())
    scored_chunks = []
    
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        common_words = query_words.intersection(chunk_words)
        
        # Calculate similarity score (0 to 1)
        if query_words:
            score = len(common_words) / len(query_words)
        else:
            score = 0.1  # Default score for empty query
        
        # Ensure score is between 0 and 1
        score = max(0.1, min(1.0, score))
        scored_chunks.append((chunk, score))
    
    # Sort by score and return top k
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:k]
@app.get("/")
async def root():
    return {"message": "🚀 RAG Knowledge Base with Groq AI is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "llm_provider": "Groq",
        "documents_loaded": len(documents_store)
    }

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    global documents_store
    documents_store = []  # Clear previous documents
    
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        file_paths = []
        
        for file in files:
            if not file.filename.lower().endswith(('.pdf', '.txt')):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
            
            # Save file
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_paths.append(file_path)
        
        # Process documents
        all_chunks = []
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            text = extract_text_from_file(file_path)
            if text.strip():
                chunks = chunk_text(text)
                all_chunks.extend(chunks)
        
        documents_store = all_chunks
        
        return {
            "message": f"✅ Successfully processed {len(files)} files",
            "chunks_created": len(all_chunks),
            "file_paths": file_paths
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")
@app.post("/query")
async def query_knowledge_base(query: dict):
    """Query the knowledge base"""
    try:
        if not documents_store:
            raise HTTPException(status_code=400, detail="Please upload documents first")
        
        user_query = query.get("question", "").strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Retrieve relevant chunks with scores
        relevant_chunks_with_scores = simple_retrieve(user_query, documents_store, k=3)
        
        if not relevant_chunks_with_scores:
            return {
                "question": user_query,
                "answer": "❌ No relevant information found in the uploaded documents.",
                "sources": []
            }
        
        # Generate answer
        prompt = llm_integration.create_rag_prompt([chunk for chunk, score in relevant_chunks_with_scores], user_query)
        answer = llm_integration.generate_answer(prompt)
        
        # Prepare sources with similarity scores
        sources = [
            {
                "source_id": i+1,
                "content": chunk[:500] + "..." if len(chunk) > 500 else chunk,
                "similarity_score": f"{score:.3f}",
                "content_length": len(chunk)
            } 
            for i, (chunk, score) in enumerate(relevant_chunks_with_scores)
        ]
        
        return {
            "question": user_query,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(relevant_chunks_with_scores)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "documents_processed": len(documents_store),
        "status": "ready" if documents_store else "waiting_for_documents"
    }

if __name__ == "__main__":
    print("🚀 Starting RAG Knowledge Base with Groq AI...")
    print("📚 API will be available at: http://localhost:8000")
    print("🔑 Make sure you have set GROQ_API_KEY in .env file")
    uvicorn.run(app, host="0.0.0.0", port=8000)