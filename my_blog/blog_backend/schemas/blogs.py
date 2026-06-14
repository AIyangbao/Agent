from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class BlogCreate(BaseModel):
    title: str
    content: str
    tag_ids: List[int]


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class BlogResponse(BaseModel):
    id: int
    title: str
    excerpt: str
    date: str
    readTime: str
    tags: List[str]

    class Config:
        from_attributes = True
