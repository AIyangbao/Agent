from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class BlogCreate(BaseModel):
    title: str
    content: str
    user_id: int
    tag_ids: Optional[List[int]] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    tags: List[str]

    class Config:
        from_attributes = True
