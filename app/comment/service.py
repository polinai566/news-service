from typing import Sequence
from sqlalchemy import select

from app.database import SessionDep
from .models import Comment
from .schemas import CommentCreate, CommentUpdate
from app.utils import check_jwt, get_privileges

class CommentService:
    def __init__(self, db: SessionDep):
        self.db = db

    # создание комментария
    async def create(self, payload: CommentCreate, jwt_token: str) -> Comment | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        new_comment = Comment(**payload.model_dump(), author_id = int(jwt_payload["user_id"]))
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment
    
    # чтение списка комментариев
    async def list(self, jwt_token: str) -> Sequence[Comment] | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        comments = await self.db.execute(select(Comment))
        return comments.scalars().all()
    
    # чтение комментария по индексу
    async def get(self, comment_id: int, jwt_token: str) -> Comment | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            return "Comment not found"
        return comment
    
    # обновление комментария
    async def update(self, comment_id: int, payload: CommentUpdate, jwt_token: str) -> Comment | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            return "Comment not found"
        rights = get_privileges(jwt_payload, comment.author_id) 
        if rights in ["admin", "author_same", "user_same"]:
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(comment, field, value)
            await self.db.commit()
            await self.db.refresh(comment)
            return comment
        else:
            return "Permission denied"
    
    # удаление комментария
    async def delete(self, comment_id: int, jwt_token: str) -> None | str:
        jwt_payload = check_jwt(jwt_token)
        if not jwt_payload:
            return "Incorrect access token"
        comment = await self.db.execute(select(Comment).where(Comment.comment_id == comment_id))
        comment = comment.scalar_one_or_none()
        if not comment:
            return "Comment not found"
        rights = get_privileges(jwt_payload, comment.author_id) 
        if rights in ["admin", "author_same", "user_same"]:
            await self.db.delete(comment)
            await self.db.commit()
            return "The comment was successfully deleted"
        else:
            return "Permission denied"