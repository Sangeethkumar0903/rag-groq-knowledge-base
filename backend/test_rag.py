import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Health Check:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("❌ Health check failed:", e)

def test_upload():
    """Test document upload"""
    print("\n🧪 Testing document upload...")
    try:
        # Create a sample text file for testing
        with open("sample_test.txt", "w") as f:
            f.write("""
            Artificial Intelligence (AI) is transforming various industries.
            
            Key Benefits of AI:
            1. Automation of repetitive tasks
            2. Data analysis and pattern recognition
            3. Natural language processing capabilities
            4. Predictive analytics and forecasting
            
            Machine Learning is a subset of AI that enables computers to learn without explicit programming.
            Deep Learning uses neural networks with multiple layers for complex pattern recognition.
            
            Conclusion: AI has the potential to revolutionize how we work and solve problems.
            """)
        
        files = [('files', ('sample_test.txt', open('sample_test.txt', 'rb'), 'text/plain'))]
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print("✅ Upload Response:", json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print("❌ Upload test failed:", e)

def test_query():
    """Test query endpoint"""
    print("\n🧪 Testing query endpoint...")
    try:
        test_questions = [
            "What are the key benefits of AI?",
            "What is machine learning?",
            "How is deep learning related to AI?"
        ]
        
        for question in test_questions:
            print(f"\n🔍 Question: {question}")
            response = requests.post(f"{BASE_URL}/query", json={"question": question})
            result = response.json()
            
            print("✅ Answer:", result.get('answer', 'No answer'))
            print("📚 Sources found:", result.get('retrieved_chunks', 0))
            
            # Brief pause between queries
            time.sleep(2)
            
    except Exception as e:
        print("❌ Query test failed:", e)

def test_stats():
    """Test stats endpoint"""
    print("\n🧪 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print("✅ Stats:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("❌ Stats test failed:", e)

if __name__ == "__main__":
    print("🚀 Starting RAG System Tests with Groq AI...")
    test_health()
    test_upload()
    test_query()
    test_stats()
    print("\n🎉 All tests completed!")