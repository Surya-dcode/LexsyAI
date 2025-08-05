# backend/init_db.py
from db.database import engine, Base
import models.client, models.document, models.email

Base.metadata.create_all(bind=engine)
