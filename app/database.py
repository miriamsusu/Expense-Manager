import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Local default is SQLite; production overrides this via the DATABASE_URL env var.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expenses.db")

# check_same_thread is a SQLite-only argument; Postgres would reject it.
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()