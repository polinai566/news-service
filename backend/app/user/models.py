from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    registration_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    avatar = Column(String, nullable=True)
    user_role = Column(String, default="user")
    password = Column(String, nullable=True)

    news = relationship("News", back_populates="author")
    comment = relationship("Comment", back_populates="author")