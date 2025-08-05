# backend/services/document_service.py

import os
from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import tempfile
from services.vector_service import add_text_to_vectorstore

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

    metadata = {"filename": file.filename, "source_type": "document"}
    add_text_to_vectorstore(client_id, content, metadata)

    return {"message": f"Uploaded and embedded {file.filename}"}
