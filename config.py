import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI 
OPENAI_API_KEY = "" #Add you own API key here
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_LLM_MODEL = "gpt-5-2025-08-07"

# Pinecone 
PINECONE_API_KEY = ""
PINECONE_INDEX_NAME = "teachable-ai"
COURSE_MATERIALS_NAMESPACE = "course_materials"
ANALYTICS_NAMESPACE = "analytics"

# Flask 
SECRET_KEY = "hellocmu1234"

# Document Processing
MAX_CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks

# Supported file types
ALLOWED_EXTENSIONS = {"txt", "pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024 