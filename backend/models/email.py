# backend/models/email.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from db.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    subject = Column(String)
    sender = Column(String)
    recipient = Column(String)
    body = Column(Text)
    date_sent = Column(DateTime)
