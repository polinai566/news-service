from pydantic import BaseModel
from datetime import datetime

class SessionBase(BaseModel):
    refresh_token_expiretime: datetime
    user_id: int

class SessionCreate(SessionBase):
    refresh_token: str
    session_id: int
    user_agent: str

class SessionRead(SessionBase):
    session_id: int
    user_agent: str

class SessionAdminRead(SessionRead):
    refresh_token: str

class SessionRefreshToken(BaseModel):
    refresh_token: str