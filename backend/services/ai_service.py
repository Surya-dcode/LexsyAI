# backend/services/ai_service.py

import os
import openai
from chromadb import PersistentClient
from config import get_settings

settings = get_settings()
CHROMA_DIR = settings.chroma_persist_dir
OPENAI_API_KEY = settings.openai_api_key

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def ask_question(client_id: int, question: str):
    # Get ChromaDB client
    chroma_client = PersistentClient(path=os.path.join(CHROMA_DIR, f"client_{client_id}"))
    
    try:
        collection = chroma_client.get_collection(name="default")
    except:
        raise ValueError(f"No documents found for client {client_id}")

    # Search for relevant documents
    results = collection.query(
        query_texts=[question],
        n_results=5
    )
    
    if not results['documents'] or not results['documents'][0]:
        return {"answer": "No relevant documents found.", "sources": []}
    
    # Combine retrieved documents
    context = "\n\n".join(results['documents'][0])
    
    # Create prompt
    prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {question}

Answer:"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant. Answer questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        answer = response.choices[0].message.content
        
        # Extract sources from metadata
        sources = []
        if results['metadatas'] and results['metadatas'][0]:
            for metadata in results['metadatas'][0]:
                if metadata.get('source_type') == 'email':
                    sources.append({"type": "email", "subject": metadata.get('subject', 'Unknown')})
                else:
                    sources.append({"type": "document", "filename": metadata.get('filename', 'Unknown')})
        
        return {"answer": answer, "sources": sources}
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
