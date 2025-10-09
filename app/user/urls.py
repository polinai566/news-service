from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.database import SessionDep
from app.user.schemas import UserCreate, UserRead, UserUpdate
from app.user.models import User

router = APIRouter(tags=["users"])

# создание пользователя (create)
@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: SessionDep):
    # проверка уникальности email
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(**user.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# чтение списка пользователей (read)
@router.get("/", response_model=list[UserRead])
async def get_users(db: SessionDep):
    users = await db.execute(select(User))
    return users.scalars().all()

# чтение пользователя по индексу (read)
@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, db: SessionDep):
    user = await db.execute(select(User).where(User.user_id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# обновление пользователя (update)
@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_update: UserUpdate, db: SessionDep):
    user = await db.execute(select(User).where(User.user_id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

# удаление пользователя (delete)
@router.delete("/{user_id}")
async def delete_user(user_id: int, db: SessionDep):
    user = await db.execute(select(User).where(User.user_id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}