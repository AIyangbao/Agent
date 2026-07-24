from pydantic import BaseModel,Field

class ChatRequest(BaseModel):
    message: str = Field(...,min_length=1)
    history: list[dict] = Field(default_factory=list)

class ChatReply(BaseModel):
    reply: str