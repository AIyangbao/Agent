from pydantic import BaseModel
from typing import Optional

class MusicResponse(BaseModel):
    id: int
    title: str
    artist: str
    cover: Optional[str] = None
    src: str

    class Config:
        from_attributes = True
        