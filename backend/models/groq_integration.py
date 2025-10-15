import os
import requests
import json
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

class GroqIntegration:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # ✅ Updated working model
    
    def create_rag_prompt(self, context: List[Tuple[str, float]], query: str) -> str:
        """Create RAG prompt with context and query"""
        context_text = "\n\n".join([f"📄 Source {i+1} (Relevance: {sim:.2f}):\n{chunk}" 
                                  for i, (chunk, sim) in enumerate(context)])
        
        prompt = f"""You are an expert AI assistant. Using ONLY the context provided below from uploaded documents, answer the user's question accurately and concisely.

IMPORTANT RULES:
1. Answer based STRICTLY on the provided context only
2. Be accurate, concise, and well-structured
3. If the context doesn't contain enough information to answer the question, say: "The documents do not contain enough information to answer this question."
4. Never make up information or use external knowledge
5. If relevant, mention which source contained the information

CONTEXT FROM DOCUMENTS:
{context_text}

USER'S QUESTION: {query}

FINAL ANSWER:"""
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        """Generate answer using Groq API via direct HTTP requests"""
        if not self.api_key:
            return "❌ Error: GROQ_API_KEY not found in environment variables"
        
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
                "max_tokens": 1024,
                "top_p": 0.9,
                "stream": False
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"❌ Groq API Error: Status {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f" - {error_detail['error'].get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                return error_msg
                
        except requests.exceptions.Timeout:
            return "❌ Error: Request timeout - Groq API took too long to respond"
        except requests.exceptions.ConnectionError:
            return "❌ Error: Connection failed - Check your internet connection"
        except Exception as e:
            return f"❌ Error: {str(e)}"