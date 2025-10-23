import requests
import json

def test_system():
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Health check
    print("1. Testing health...")
    health = requests.get(f"{BASE_URL}/health")
    print(f"   Health: {health.status_code}")
    print(f"   Response: {health.json()}")
    
    # Test 2: Create test document
    test_content = """
    Associate Developer Role Description:
    
    An Associate Developer is an entry-level software development position.
    Key responsibilities include:
    - Writing and testing code
    - Debugging applications
    - Participating in code reviews
    - Collaborating with team members
    
    Required skills:
    - Programming languages like Python, Java, or JavaScript
    - Basic understanding of databases
    - Problem-solving skills
    - Version control with Git
    
    This role typically requires a bachelor's degree in computer science or related field.
    """
    
    # Test 3: Upload document
    print("\n2. Testing document upload...")
    files = {
        'files': ('test_developer.txt', test_content, 'text/plain')
    }
    upload = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"   Upload: {upload.status_code}")
    print(f"   Response: {upload.json()}")
    
    # Test 4: Query the system
    print("\n3. Testing query...")
    test_queries = [
        "What is an Associate Developer?",
        "What are the key responsibilities?",
        "What skills are required?"
    ]
    
    for query in test_queries:
        print(f"   Query: {query}")
        response = requests.post(f"{BASE_URL}/query", json={"question": query})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Answer: {result['answer'][:100]}...")
            print(f"   📚 Sources: {len(result['sources'])}")
            if result['sources']:
                for source in result['sources']:
                    print(f"      - Score: {source.get('similarity_score', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.json()}")
        print()

if __name__ == "__main__":
    test_system()