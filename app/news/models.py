from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class News(Base):
    __tablename__ = "news"

    news_id = Column(Integer, primary_key=True, index=True)
    header = Column(String, index=True, nullable=False)
    content = Column(JSON, nullable=False)
    publication_date = Column(DateTime, default=datetime.now)
    author_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    cover = Column(String, nullable=True)

    author = relationship("User", back_populates="news", lazy="subquery")
    comment = relationship("Comment", back_populates="news", cascade="all, delete-orphan", lazy="subquery")