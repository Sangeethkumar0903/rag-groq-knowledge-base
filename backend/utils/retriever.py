import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, embedder):
        self.embedder = embedder
    
    def get_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query"""
        try:
            if hasattr(self.embedder, 'embedding_model'):
                # Using sentence-transformers
                embedding = self.embedder.embedding_model.encode([query])
                return embedding[0].tolist()
            else:
                # Fallback: simple TF-IDF or other approach
                # For now, return a dummy embedding to avoid errors
                logger.warning("Using fallback embedding method")
                return [0.1] * 384  # Default dimension
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            # Return a simple fallback embedding
            return [0.1] * 384
    
    def retrieve_similar_chunks(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve top-k most similar chunks"""
        try:
            # Check if using TF-IDF approach
            if hasattr(self.embedder, 'retrieve_similar_chunks'):
                return self.embedder.retrieve_similar_chunks(query, k)
            
            # Using FAISS approach
            if self.embedder.index is None or not self.embedder.chunks:
                logger.error("No index or chunks available")
                return []
            
            query_embedding = self.get_query_embedding(query)
            
            # Ensure embedding is the right type and shape
            if not isinstance(query_embedding, list):
                logger.error(f"Invalid embedding type: {type(query_embedding)}")
                return []
            
            # Convert to numpy array and search
            query_vector = np.array([query_embedding]).astype('float32')
            
            # Ensure the vector has the right dimensions
            if query_vector.shape[1] != self.embedder.index.d:
                logger.error(f"Embedding dimension mismatch: {query_vector.shape[1]} vs {self.embedder.index.d}")
                return []
            
            # Search for similar chunks
            distances, indices = self.embedder.index.search(query_vector, k)
            
            # Get chunks and their similarity scores
            results = []
            for i, idx in enumerate(indices[0]):
                if 0 <= idx < len(self.embedder.chunks):
                    chunk = self.embedder.chunks[idx]
                    # Convert distance to similarity score (ensure it's a float)
                    try:
                        similarity = float(1 / (1 + distances[0][i]))
                    except (ValueError, TypeError, ZeroDivisionError):
                        similarity = 0.5  # Default similarity
                    results.append((chunk, similarity))
            
            logger.info(f"Retrieved {len(results)} chunks for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieve_similar_chunks: {e}")
            return []