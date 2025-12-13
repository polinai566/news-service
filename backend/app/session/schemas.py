from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SessionBase(BaseModel):
    user_id: int
    refresh_token_expiretime: datetime

class SessionCreate(SessionBase):
    refresh_token: str
    user_agent: str
    model_config = ConfigDict(from_attributes=True)

class SessionRead(SessionBase):
    user_agent: str

class SessionAdminRead(SessionRead):
    refresh_token: str

class SessionRefreshToken(BaseModel):
    refresh_token: str