from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    news_id: int

class CommentUpdate(CommentBase):
    pass

class CommentRead(CommentBase):
    comment_id: int
    news_id: int
    author_id: int
    publication_date: datetime
    model_config = ConfigDict(from_attributes=True)