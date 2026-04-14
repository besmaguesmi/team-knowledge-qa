import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Get from console.groq.com
    # If using Gemini: GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

settings = Settings()