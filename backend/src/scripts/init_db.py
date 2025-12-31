

from sqlmodel import SQLModel
from models.user import USER
from db.database import engine, get_session


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully!")


def create_user():
    with get_session() as session:
        user = USER(name="John Doe", email="john.doe@example.com", password="password")
        session.add(user)
        session.commit()
        print(f"✅ User {user.name} created successfully!")

if __name__ == "__main__":
    create_tables()
    create_user()