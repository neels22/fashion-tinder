# test_db_connection.py
from sqlmodel import Session
from sqlalchemy import text

from database import engine

def test_connection():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).first()
        print("DB connection OK:", result)

if __name__ == "__main__":
    test_connection()
