from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from ..database import Base
from dotenv import load_dotenv
import os

load_dotenv()

LIFETIME = int(str(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS")))

class Session(Base):
    __tablename__ = "session"

    session_id  = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String, index=True)
    refresh_token_lifetime = Column(DateTime, default=datetime.now()+timedelta(days=LIFETIME))
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    user_agent = Column(String, nullable=False)

    user = relationship("User", back_populates="session", lazy="subquery")