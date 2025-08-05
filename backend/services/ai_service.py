# backend/services/ai_service.py

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma")
from config import get_settings
settings = get_settings()
OPENAI_API_KEY = settings.openai_api_key

embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)

def ask_question(client_id: int, question: str):
    vector_path = os.path.join(CHROMA_DIR, f"client_{client_id}")
    if not os.path.exists(vector_path):
        raise ValueError(f"No vector store found for client {client_id}")

    vectordb = Chroma(persist_directory=vector_path, embedding_function=embedding_model)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    result = qa({"query": question})
    answer = result["result"]
    sources = []

    for doc in result["source_documents"]:
        metadata = doc.metadata
        if metadata.get("source_type") == "email":
            sources.append({"type": "email", "subject": metadata.get("subject")})
        else:
            sources.append({"type": "document", "filename": metadata.get("filename")})

    return {"answer": answer, "sources": sources}