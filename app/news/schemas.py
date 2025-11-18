from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any

class NewsBase(BaseModel):
    header: str
    content: Any
    cover: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsUpdate(NewsBase):
    pass

class NewsRead(NewsBase):
    news_id: int
    publication_date: datetime
    author_id: int
    model_config = ConfigDict(from_attributes=True)