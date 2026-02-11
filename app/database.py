import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:Qsefthuko321!@#@db:5432/book_db")

def get_engine():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            # Check if connection is actually working
            engine.connect()
            return engine
        except OperationalError:
            retries -= 1
            print(f"Database not ready... retrying in 5 seconds ({retries} retries left)")
            time.sleep(5)
    raise Exception("Could not connect to the database")

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

