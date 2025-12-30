

from sqlmodel import SQLModel
from models.user import USER
from db.database import engine

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()