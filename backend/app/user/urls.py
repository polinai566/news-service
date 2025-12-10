from fastapi import APIRouter, Depends
from .schemas import UserCreate, UserRead, UserUpdate
from .service import UserService

router = APIRouter(tags=["users"])

async def user_service(service: UserService = Depends()) -> UserService:
    return service

@router.post("/", response_model=UserRead)
async def create_user(payload: UserCreate, service: UserService = Depends(user_service)):
    return await service.create(payload)

@router.get("/", response_model=list[UserRead])
async def get_users(service: UserService = Depends(user_service)):
    return await service.list()

@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, service: UserService = Depends(user_service)):
    return await service.get(user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, service: UserService = Depends(user_service)):
    return await service.update(user_id, payload)

@router.delete("/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends(user_service)):
    return await service.delete(user_id)