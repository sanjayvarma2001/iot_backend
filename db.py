
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://user:password@127.0.0.1:3306/iot_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit= False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()