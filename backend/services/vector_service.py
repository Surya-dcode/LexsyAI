# backend/services/vector_service.py

import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from config import get_settings
settings = get_settings()

CHROMA_DIR = settings.chroma_persist_dir
OPENAI_API_KEY = settings.openai_api_key

embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def get_client_vectordb(client_id: int) -> Chroma:
    """Returns the Chroma vector DB for a specific client."""
    vector_path = os.path.join(CHROMA_DIR, f"client_{client_id}")
    os.makedirs(vector_path, exist_ok=True)
    return Chroma(persist_directory=vector_path, embedding_function=embedding_model)


def add_text_to_vectorstore(client_id: int, text: str, metadata: dict):
    db = get_client_vectordb(client_id)
    db.add_texts([text], [metadata])


def similarity_search(client_id: int, query: str, k: int = 5):
    db = get_client_vectordb(client_id)
    return db.similarity_search(query, k=k)
