from fastapi import APIRouter,Depends,Query
from schemas.ai import ChatRequest, ChatReply
import json
import asyncio
from rag.retrieve import retrieve
from fastapi.responses import StreamingResponse
from utils.auth import get_current_user
from utils.response import success_response, error_response
from curd.chat_history import save_message,get_history,clear_history
from services.ratelimit_service import ai_rate_limited
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter(prefix="/api/ai",tags=["ai"])

@router.post("/chat")
async def chat(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if await ai_rate_limited(current_user.id):
       return error_response(code=429,message="提问太频繁啦,休息一下再试", data= None)

    # —— 新增：从 DB 读最近对话，作为唯一历史来源 ——
    rows = await get_history(db, current_user.id, limit=200)
    db_history = [
       {"role": r.role, "content": r.content}
       for r in rows[-10:]
    ]
    from services.agent_service import AgentService
    agent = AgentService()
    full_reply = []
    await save_message(db,current_user.id,"user",req.message) # 先存用户消息

    # RAG检索: 同步阻塞IO丢进线程池, 不卡事件循环
    try:
       rag = await asyncio.to_thread(retrieve, req.message)
       rag_context = rag["context"]
       citations = rag["citations"]
    except Exception:
       rag_context = None # 检索挂了也能聊天
       citations = [] 


    async def event_gen():
      try:
        async for token in agent.chat_stream(req.message, db_history,rag_context=rag_context, user_id=current_user.id):
           full_reply.append(token)
           yield f"data: {json.dumps({'reply':token},ensure_ascii=False)}\n\n"
      except Exception as e:
         yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
      finally:
         await save_message(db, current_user.id,"assistant","".join(full_reply))
         # 流结束前,把引用来源推给前端
         if citations:
            yield f"data: {json.dumps({'citations':citations},ensure_ascii=False)}\n\n"
    return StreamingResponse(
       event_gen(),
       media_type="text/event-stream",
       headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.delete("/history")
async def clear(current_user: dict = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
   await clear_history(db, current_user.id)
   return success_response(message="已清空对话历史")

@router.get("/history")
async def history(limit: int = Query(50, ge=1, le=200),
                  current_user: dict = Depends(get_current_user),
                  db: AsyncSession = Depends(get_db)):
   rows = await get_history(db,current_user.id,limit)
   data = [{"role": r.role, "content": r.content} for r in rows]
   return success_response(data=data)
