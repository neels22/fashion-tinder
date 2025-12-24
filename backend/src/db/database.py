import os
import dotenv
from sqlmodel import Session, create_engine
from typing import Generator
dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")
engine = create_engine(DATABASE_URL, echo=True,pool_pre_ping=True)


def get_session()-> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
