from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    registration_date = Column(DateTime, default=datetime.now)
    is_verified = Column(Boolean, default=False) # верифицирован ли как автор?
    avatar = Column(String, nullable=True)

    news = relationship("News", back_populates="author")
    comment = relationship("Comment", back_populates="author")