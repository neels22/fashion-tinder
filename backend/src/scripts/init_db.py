

from sqlmodel import SQLModel, select
from ..models.user import USER
from ..db.database import engine, get_session


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully!")

def create_user(user: USER):
    with get_session() as session:
        session.add(user)
        session.commit()
        session.refresh(user)  # This populates the id and timestamps
        print(f"✅ User {user.name} created successfully!")
        return user

def read_users():
    with get_session() as session:
        statement = select(USER)
        result = session.exec(statement).all()
        # for user in result:
        #     print(f"User: {user.name}, Email: {user.email}")
        print(result)
        return result


if __name__ == "__main__":
    # create_tables()
    # create_user()
    read_users()