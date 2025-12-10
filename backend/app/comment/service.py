from typing import Sequence
from fastapi import HTTPException
from sqlalchemy import select

from app.database import SessionDep
from .models import Comment
from .schemas import CommentCreate, CommentUpdate

class CommentService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание комментария
    async def create(self, payload: CommentCreate) -> Comment:
        new_comment = Comment(**payload.model_dump())
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment
    
    # чтение списка комментариев
    async def list(self) -> Sequence[Comment]:
        comments = await self.db.execute(select(Comment))
        return comments.scalars().all()
    
    # чтение комментария по индексу
    async def get(self, comment_id: int) -> Comment:
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
    
    # обновление комментария
    async def update(self, comment_id: int, payload: CommentUpdate) -> Comment:
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        
        await self.db.commit()
        await self.db.refresh(comment)
        return comment
    
    # удаление комментария
    async def delete(self, comment_id: int) -> None:
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        await self.db.delete(comment)
        await self.db.commit()