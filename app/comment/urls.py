from fastapi import APIRouter, Depends
from .schemas import CommentCreate, CommentRead, CommentUpdate
from .service import CommentService

router = APIRouter(tags=["comments"])

async def comment_service(service: CommentService = Depends()) -> CommentService:
    return service

@router.post("/", response_model=CommentRead)
async def create_order(payload: CommentCreate, service: CommentService = Depends(comment_service)):
    return await service.create(payload)

@router.get("/", response_model=list[CommentRead])
async def get_comments(service: CommentService = Depends(comment_service)):
    return await service.list()

@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment_by_id(comment_id: int, service: CommentService = Depends(comment_service)):
    return await service.get(comment_id)

@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(comment_id: int, payload: CommentUpdate, service: CommentService = Depends(comment_service)):
    return await service.update(comment_id, payload)

@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, service: CommentService = Depends(comment_service)):
    return await service.delete(comment_id)