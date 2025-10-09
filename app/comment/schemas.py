from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.user.schemas import UserRead

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    news_id: int
    author_id: int

class CommentUpdate(CommentBase):
    pass

class CommentRead(CommentBase):
    comment_id: int
    news_id: int
    publication_date: datetime
    author: UserRead
    model_config = ConfigDict(from_attributes=True)