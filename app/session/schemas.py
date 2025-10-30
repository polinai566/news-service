from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SessionBase(BaseModel):
    refresh_token: str
    refresh_token_lifetime: datetime
    user_id: int

class SessionRead(SessionBase):
    session_id: int
    user_agent: str
    model_config = ConfigDict(from_attributes=True)

class SessionRefreshToken(BaseModel):
    refresh_token: str

# class SessionCreateResponse(BaseModel):
#     refresh_token: str
#     refresh_token_lifetime: datetime