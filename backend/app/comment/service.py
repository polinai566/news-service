from typing import Sequence
from sqlalchemy import select
from fastapi import HTTPException, status
from app.database import SessionDep
from .models import Comment
from .schemas import CommentCreate, CommentUpdate, CommentIdResponse

class CommentService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание комментария
    async def create(self, payload: CommentCreate, user_id: int) -> CommentIdResponse:
        new_comment = Comment(**payload.model_dump(), author_id = user_id)
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return {"comment_id": new_comment.comment_id}
    
    # чтение списка комментариев конкретной новости
    async def list(self, news_id) -> Sequence[Comment]:
        comments = await self.db.execute(select(Comment).where(Comment.news_id == news_id))
        comments_list = comments.scalars().all()
        return comments_list
    
    # чтение комментария по индексу
    async def get(self, comment_id: int) -> Comment:
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return comment
    
    # обновление комментария
    async def update(self, comment, payload: CommentUpdate) -> CommentIdResponse:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        await self.db.commit()
        await self.db.refresh(comment)
        return {"comment_id": comment.comment_id}
    
    # удаление комментария
    async def delete(self, comment) -> str:
        await self.db.delete(comment)
        await self.db.commit()
        return "The comment was successfully deleted"