from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from ..database import SessionDep
from .schemas import CommentRead, CommentCreate, CommentUpdate
from .models import Comment

router = APIRouter()

# создание комментария (create)
@router.post("/", response_model=CommentRead)
async def create_order(comment: CommentCreate, db: SessionDep):
    new_comment = Comment(**comment.model_dump())
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

# чтение списка комментариев (read)
@router.get("/", response_model=list[CommentRead])
async def get_comments(db: SessionDep):
    comments = await db.execute(select(Comment))
    return comments.scalars().all()

# чтение комментария по индексу (read)
@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment_by_id(comment_id: int, db: SessionDep):
    comment = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = comment.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

# обновление комментария (update)
@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(comment_id: int, comment_update: CommentUpdate, db: SessionDep):
    comment = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = comment.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    for field, value in comment_update.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    
    await db.commit()
    await db.refresh(comment)
    return comment

# удаление комментария (delete)
@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, db: SessionDep):
    comment = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = comment.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}