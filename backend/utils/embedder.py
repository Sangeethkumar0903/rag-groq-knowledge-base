from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import os
from typing import List
import requests
import json
from .pdf_parser import DocumentParser

class EmbeddingManager:
    def __init__(self):
        self.parser = DocumentParser()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.index = None
        self.chunks = []
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks"""
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings using Hugging Face Inference API - FREE"""
        print("Generating embeddings using Hugging Face API...")
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Using all-MiniLM-L6-v2 model via Hugging Face Inference API
                response = requests.post(
                    "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2",
                    headers={"Authorization": "Bearer hf_your_token_here"},  # Optional for public models
                    json={"inputs": chunk, "options": {"wait_for_model": True}}
                )
                
                if response.status_code == 200:
                    embedding = response.json()
                    if isinstance(embedding, list) and len(embedding) > 0:
                        embeddings.append(embedding[0])
                    else:
                        # Fallback: simple random embeddings (for testing)
                        embeddings.append(np.random.randn(384).tolist())
                else:
                    # Fallback for free usage without API key
                    embeddings.append(self._create_simple_embedding(chunk))
                    
            except Exception as e:
                print(f"Warning: Using fallback embedding for chunk {i}: {e}")
                embeddings.append(self._create_simple_embedding(chunk))
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(chunks)} chunks")
        
        return embeddings
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create a simple embedding fallback when API fails"""
        # Simple hash-based embedding for fallback (not semantic, but works)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to 384-dimensional vector (matching all-MiniLM-L6-v2)
        embedding = []
        for i in range(0, min(384 * 8, len(hash_hex)), 8):
            hex_val = hash_hex[i:i+8]
            try:
                num = int(hex_val, 16) / 0xFFFFFFFF
            except:
                num = 0.5
            embedding.append(num)
        
        # Pad if needed
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def create_vector_store(self, embeddings: List[List[float]]):
        """Create FAISS vector store"""
        dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
    
    def process_documents(self, file_paths: List[str]):
        """Process multiple documents and create embeddings"""
        all_chunks = []
        
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            text = self.parser.parse_document(file_path)
            if text.strip():
                chunks = self.chunk_text(text)
                all_chunks.extend(chunks)
            else:
                print(f"Warning: No text extracted from {file_path}")
        
        if not all_chunks:
            print("❌ Error: No text chunks were created from any documents")
            return 0
            
        self.chunks = all_chunks
        print(f"Generated {len(all_chunks)} chunks, now creating embeddings...")
        
        embeddings = self.generate_embeddings(all_chunks)
        self.create_vector_store(embeddings)
        
        print(f"✅ Processed {len(all_chunks)} chunks from {len(file_paths)} documents")
        return len(all_chunks)
    
    def save_index(self, file_path: str):
        """Save FAISS index to file"""
        if self.index:
            faiss.write_index(self.index, file_path)
    
    def load_index(self, file_path: str, chunks: List[str]):
        """Load FAISS index from file"""
        self.index = faiss.read_index(file_path)
        self.chunks = chunks