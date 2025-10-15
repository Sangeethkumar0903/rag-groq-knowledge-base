import os
import requests
from dotenv import load_dotenv

load_dotenv()

def discover_available_models():
    """Discover available Groq models"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return []
    
    url = "https://api.groq.com/openai/v1/models"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Discovering available models...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            models_data = response.json()
            available_models = []
            
            print("✅ Available models:")
            for model in models_data.get('data', []):
                model_id = model.get('id', '')
                if model_id:
                    print(f"   - {model_id}")
                    available_models.append(model_id)
            
            return available_models
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_specific_models():
    """Test specific models that are likely available"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        return
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Newer models that might be available
    potential_models = [
        "llama-3.1-8b-instant",    # New Llama 3.1 models
        "llama-3.1-70b-versatile",
        "llama-3.2-1b-preview",    # Llama 3.2 models
        "llama-3.2-3b-preview",
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
        "mixtral-8x7b-32768",      # Try original name
        "gemma2-9b-it"             # Gemma 2 models
    ]
    
    print("\n🧪 Testing potential models...")
    working_models = []
    
    for model in potential_models:
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello' in one word."
                }
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                print(f"✅ WORKING: {model}")
                print(f"   Response: {answer}")
                working_models.append(model)
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"   ❌ {model}: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ {model}: Error - {e}")
    
    return working_models

if __name__ == "__main__":
    print("🚀 Groq Model Discovery Tool")
    print("=" * 50)
    
    # First, discover all available models
    available_models = discover_available_models()
    
    # Then test specific potential models
    working_models = test_specific_models()
    
    if working_models:
        print(f"\n🎉 Working models found: {working_models}")
        print(f"\n💡 Update your groq_integration.py with one of these models:")
        for model in working_models:
            print(f'   self.model = "{model}"')
    else:
        print("\n❌ No working models found. Please check:")
        print("   - Your Groq API key is valid")
        print("   - You have access to models in Groq Console")
        print("   - Visit: https://console.groq.com")