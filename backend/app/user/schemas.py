from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    user_role: str = "user"
    avatar: Optional[str] = None
    password: Optional[str] = None

class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password: str
    avatar: Optional[str] = None

class UserUpdate(UserBase):
    pass

class UserRead(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr
    user_role: str
    avatar: Optional[str] = None
    registration_date: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserIdResponse(BaseModel):
    user_id: int