from fastapi import APIRouter,Depends,Query
from schemas.ai import ChatRequest, ChatReply
import json
from fastapi.responses import StreamingResponse
from services.agent_service import AgentService
from utils.auth import get_current_user
from utils.response import success_response, error_response
router = APIRouter(prefix="/api/ai",tags=["ai"])

@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    agent = AgentService()
    
    async def event_gen():
      try:
        async for token in agent.chat_stream(req.message, req.history):
           yield f"data: {json.dumps({'reply':token},ensure_ascii=False)}\n\n"
      except Exception as e:
         yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
       event_gen(),
       media_type="text/event-stream",
       headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )