from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "Employee"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    position = Column(String, unique=False, nullable=False)
    contact = Column(String, unique=False, nullable=False)
    age = Column(Integer, unique=False, nullable=False)
    salary = Column(Float, unique=False, nullable=False)

