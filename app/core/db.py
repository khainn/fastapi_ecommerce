import os
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
