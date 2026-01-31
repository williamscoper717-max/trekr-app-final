from database import engine, Base
from models.user import User
from models.code import Code
from models.trip import Trip
from models.program import Program
from models.tip import Tip
from models.adem import Adem

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
