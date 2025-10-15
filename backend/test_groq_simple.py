import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq_api():
    """Test Groq API with the working model"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use the working model
    model = "llama-3.1-8b-instant"
    
    print(f"🧪 Testing Groq API with model: {model}")
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello World' in one sentence and tell me what 2+2 equals."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"✅ Groq API test successful!")
            print(f"🤖 Response: {answer}")
            return True
        else:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"❌ API Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_groq_api()