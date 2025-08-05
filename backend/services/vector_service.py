# backend/services/vector_service.py

import os
import openai
from chromadb import PersistentClient
from config import get_settings

settings = get_settings()
CHROMA_DIR = settings.chroma_persist_dir
OPENAI_API_KEY = settings.openai_api_key

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def get_embedding(text: str):
    """Get OpenAI embedding for text"""
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def get_client_vectordb(client_id: int):
    """Returns the ChromaDB client for a specific client."""
    vector_path = os.path.join(CHROMA_DIR, f"client_{client_id}")
    os.makedirs(vector_path, exist_ok=True)
    
    client = PersistentClient(path=vector_path)
    
    # Get or create collection
    try:
        collection = client.get_collection(name="default")
    except:
        collection = client.create_collection(name="default")
    
    return collection

def add_text_to_vectorstore(client_id: int, text: str, metadata: dict):
    """Add text to vector store"""
    collection = get_client_vectordb(client_id)
    
    # Generate embedding
    embedding = get_embedding(text)
    
    # Add to collection
    collection.add(
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
        ids=[f"doc_{len(collection.get()['ids']) + 1}"]
    )

def similarity_search(client_id: int, query: str, k: int = 5):
    """Search for similar documents"""
    collection = get_client_vectordb(client_id)
    
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    
    return results
