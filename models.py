from sqlalchemy import Column, Integer, String
from database import Base

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    code = Column(String, unique=True)
    guests_allowed = Column(Integer)
    guests_confirmed = Column(Integer, default=0)

    guest_names = Column(String)
