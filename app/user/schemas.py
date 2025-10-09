from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    is_verified: bool = False
    avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserRead(UserBase):
    user_id: int
    registration_date: datetime
    model_config = ConfigDict(from_attributes=True)