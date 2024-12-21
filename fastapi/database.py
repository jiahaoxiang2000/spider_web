from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///spider.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    total_page = Column(Integer, default=10)
    current_page = Column(Integer, default=0)
    stop_flag = Column(Boolean, default=False)
    done = Column(Boolean, default=False)
    data_file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class AccountDB(Base):
    __tablename__ = "accounts"

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    is_online = Column(Boolean, default=False, server_default="0")
    is_active = Column(Boolean, default=True, server_default="1")


def init_db():
    Base.metadata.create_all(bind=engine)


# Create tables at module import
init_db()
