import subprocess
import sys
import os
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not groq_key:
        print("❌ GROQ_API_KEY not found in .env file")
        print("🔑 Please get your free API key from: https://console.groq.com")
        print("💡 Then add it to your .env file: GROQ_API_KEY=your_key_here")
        return False
    else:
        print("✅ GROQ_API_KEY found")
        return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_sample_data():
    """Create sample data directory"""
    os.makedirs("../data/sample_docs", exist_ok=True)
    print("✅ Created sample data directory")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Start the backend server:")
    print("   cd backend && python main.py")
    print("2. In a new terminal, start the frontend:")
    print("   streamlit run frontend/app.py")
    print("3. Open your browser to: http://localhost:8501")
    print("4. Upload documents and start asking questions!")
    print("\n💡 Make sure your GROQ_API_KEY is in the .env file")

if __name__ == "__main__":
    print("🔧 Setting up RAG Knowledge Base with Groq AI...")
    
    if check_environment() and install_requirements():
        create_sample_data()
        print_next_steps()
    else:
        print("❌ Setup failed. Please check the errors above.")