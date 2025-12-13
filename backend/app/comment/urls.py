from fastapi import APIRouter, Depends
from .schemas import CommentCreate, CommentRead, CommentUpdate
from .service import CommentService
from .models import Comment
from app.depends import get_jwt_payload, same_comment_author_or_admin

router = APIRouter(tags=["comments"])

async def comment_service(service: CommentService = Depends()) -> CommentService:
    return service

@router.post("/", response_model=CommentRead)
async def create_comment(payload: CommentCreate, service: CommentService = Depends(comment_service), jwt_payload = Depends(get_jwt_payload)):
    return await service.create(payload, int(jwt_payload["user_id"]))

@router.get("/news/{news_id}", response_model=list[CommentRead])
async def get_comments(news_id: int, service: CommentService = Depends(comment_service)):
    return await service.list(news_id)

@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment_by_id(comment_id: int, service: CommentService = Depends(comment_service)):
    return await service.get(comment_id)

@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(comment_id: int, payload: CommentUpdate, service: CommentService = Depends(comment_service), comment: Comment = Depends(same_comment_author_or_admin)):
    return await service.update(comment, payload)

@router.delete("/{comment_id}", response_model=str)
async def delete_comment(comment_id: int, service: CommentService = Depends(comment_service), comment: Comment = Depends(same_comment_author_or_admin)):
    return await service.delete(comment)