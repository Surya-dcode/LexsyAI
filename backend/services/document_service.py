# backend/services/document_service.py

import os
from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import tempfile
from config import get_settings

# Get settings from config
settings = get_settings()
CHROMA_DIR = settings.chroma_persist_dir
OPENAI_API_KEY = settings.openai_api_key

embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def process_document_upload(client_id: int, file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    content = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        if ext == "pdf":
            reader = PdfReader(tmp_path)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif ext == "docx":
            doc = DocxDocument(tmp_path)
            content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        elif ext == "txt":
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            raise ValueError("Unsupported file type")
    finally:
        os.unlink(tmp_path)

    if not content.strip():
        raise ValueError("Uploaded file is empty or could not be parsed")

    vector_path = os.path.join(CHROMA_DIR, f"client_{client_id}")
    os.makedirs(vector_path, exist_ok=True)

    metadata = {"filename": file.filename, "source_type": "document"}

    vectordb = Chroma(persist_directory=vector_path, embedding_function=embedding_model)
    vectordb.add_texts(
        texts=[content],
        metadatas=[metadata]
    )

    return {"message": f"Uploaded and embedded {file.filename}"}
