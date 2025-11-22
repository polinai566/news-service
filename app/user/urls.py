from fastapi import APIRouter, Depends
from .schemas import UserCreate, UserRead, UserUpdate
from .service import UserService
from app.depends import is_admin, same_user_or_admin

router = APIRouter(tags=["users"])

async def user_service(service: UserService = Depends()) -> UserService:
    return service

@router.post("/", response_model=UserRead | str)
async def register_user(payload: UserCreate, service: UserService = Depends(user_service)):
    return await service.create(payload)

@router.get("/", response_model=list[UserRead])
async def get_users(service: UserService = Depends(user_service), _ = Depends(is_admin)):
    return await service.list()

@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, service: UserService = Depends(user_service), _ = Depends(same_user_or_admin)):
    return await service.get(user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, service: UserService = Depends(user_service), _ = Depends(same_user_or_admin)):
    return await service.update(user_id, payload)

@router.delete("/{user_id}", response_model=str)
async def delete_user(user_id: int, service: UserService = Depends(user_service), _ = Depends(same_user_or_admin)):
    return await service.delete(user_id)