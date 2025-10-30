from fastapi import APIRouter, Depends
from .schemas import UserCreate, UserRead, UserUpdate
from .service import UserService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["users"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def user_service(service: UserService = Depends()) -> UserService:
    return service

@router.post("/", response_model=UserRead | str)
async def register_user(payload: UserCreate, service: UserService = Depends(user_service)):
    return await service.create(payload)

@router.get("/", response_model=list[UserRead] | str)
async def get_users(service: UserService = Depends(user_service), jwt_token: str = Depends(oauth2)):
    return await service.list(jwt_token)

@router.get("/{user_id}", response_model=UserRead | str)
async def get_user_by_id(user_id: int, service: UserService = Depends(user_service), jwt_token: str = Depends(oauth2)):
    return await service.get(user_id, jwt_token)

@router.put("/{user_id}", response_model=UserRead | str)
async def update_user(user_id: int, payload: UserUpdate, service: UserService = Depends(user_service), jwt_token: str = Depends(oauth2)):
    return await service.update(user_id, payload, jwt_token)

@router.delete("/{user_id}", response_model=None | str)
async def delete_user(user_id: int, service: UserService = Depends(user_service), jwt_token: str = Depends(oauth2)):
    return await service.delete(user_id, jwt_token)