from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    registration_date = Column(DateTime, default=datetime.now)
    avatar = Column(String, nullable=True)
    user_role = Column(String, default="user")
    password = Column(String, nullable=False)

    news = relationship("News", back_populates="author")
    comment = relationship("Comment", back_populates="author")
    session = relationship("Session", back_populates="user")