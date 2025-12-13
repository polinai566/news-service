from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Comment(Base):
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    news_id = Column(Integer, ForeignKey("news.news_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    publication_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    news = relationship("News", back_populates="comment", lazy="subquery")
    author = relationship("User", back_populates="comment", lazy="subquery")
