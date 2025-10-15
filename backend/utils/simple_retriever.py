import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class SimpleRetriever:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.tfidf_matrix = None
        
        if chunks:
            self._fit_vectorizer()
    
    def _fit_vectorizer(self):
        """Fit the TF-IDF vectorizer with the chunks"""
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
            logger.info(f"TF-IDF vectorizer fitted with {len(self.chunks)} chunks")
        except Exception as e:
            logger.error(f"Error fitting TF-IDF vectorizer: {e}")
    
    def retrieve_similar_chunks(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve similar chunks using TF-IDF cosine similarity"""
        try:
            if self.tfidf_matrix is None or not self.chunks:
                logger.error("No TF-IDF matrix or chunks available")
                return []
            
            # Transform query to TF-IDF
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarities
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top-k chunks
            top_indices = similarities.argsort()[-k:][::-1]
            
            results = []
            for idx in top_indices:
                if 0 <= idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    similarity = float(similarities[idx])  # Ensure it's a float
                    results.append((chunk, similarity))
            
            logger.info(f"Retrieved {len(results)} chunks using TF-IDF")
            return results
            
        except Exception as e:
            logger.error(f"Error in TF-IDF retrieval: {e}")
            # Fallback: return first k chunks
            return [(chunk, 0.5) for chunk in self.chunks[:k]]