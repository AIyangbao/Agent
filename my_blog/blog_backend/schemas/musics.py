from pydantic import BaseModel, ConfigDict
from typing import Optional

class MusicResponse(BaseModel):
    id: int
    title: str
    artist: str
    cover: Optional[str] = None
    src: str
    model_config = ConfigDict(from_attributes=True)
        