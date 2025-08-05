# backend/models/document.py
from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    filename = Column(String)
    file_type = Column(String)
    processing_status = Column(String, default="completed")
