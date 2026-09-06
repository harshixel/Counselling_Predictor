"""
models.py

SQLAlchemy schema for colleges, branches, and round-wise cutoffs.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)

    branches = relationship("Branch", back_populates="college")


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)

    college = relationship("College", back_populates="branches")
    cutoffs = relationship("Cutoff", back_populates="branch")


class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    category = Column(String, nullable=False)   # e.g. "General", "OBC", "EWS"
    round = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    rank = Column(Integer)
    percentile = Column(Float)

    branch = relationship("Branch", back_populates="cutoffs")


def get_engine(db_path: str = "sqlite:///counselling.db"):
    return create_engine(db_path)


def init_db(db_path: str = "sqlite:///counselling.db"):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
