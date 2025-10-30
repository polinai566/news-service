from fastapi import APIRouter, Depends
from .schemas import CommentCreate, CommentRead, CommentUpdate
from .service import CommentService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["comments"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def comment_service(service: CommentService = Depends()) -> CommentService:
    return service

@router.post("/", response_model=CommentRead | str)
async def create_order(payload: CommentCreate, service: CommentService = Depends(comment_service), jwt_token: str = Depends(oauth2)):
    return await service.create(payload, jwt_token)

@router.get("/", response_model=list[CommentRead] | str)
async def get_comments(service: CommentService = Depends(comment_service), jwt_token: str = Depends(oauth2)):
    return await service.list(jwt_token)

@router.get("/{comment_id}", response_model=CommentRead | str)
async def get_comment_by_id(comment_id: int, service: CommentService = Depends(comment_service), jwt_token: str = Depends(oauth2)):
    return await service.get(comment_id, jwt_token)

@router.put("/{comment_id}", response_model=CommentRead | str)
async def update_comment(comment_id: int, payload: CommentUpdate, service: CommentService = Depends(comment_service), jwt_token: str = Depends(oauth2)):
    return await service.update(comment_id, payload, jwt_token)

@router.delete("/{comment_id}", response_model=None | str)
async def delete_comment(comment_id: int, service: CommentService = Depends(comment_service), jwt_token: str = Depends(oauth2)):
    return await service.delete(comment_id, jwt_token)