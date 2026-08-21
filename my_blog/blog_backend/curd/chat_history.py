from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat_history import ChatHistory

async def save_message(db: AsyncSession, user_id: int, role: str, content: str):
    msg = ChatHistory(user_id=user_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_history(db: AsyncSession, user_id: int, limit: int = 50):
    stmt = (select(ChatHistory).where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.id.asc()).limit(limit))
    return (await db.execute(stmt)).scalars().all()

async def clear_history(db: AsyncSession, user_id: int):
    rows = (await db.execute(select(ChatHistory).where(ChatHistory.user_id == user_id))).scalars().all()
    for r in rows:
        await db.delete(r)
    await db.commit()

async def get_recent_history(db, user_id, n=10):
    # 先按 id 倒序取最近 n 条，再反转成升序（符合 _build_messages 期望的正序）
    stmt = (select(ChatHistory).where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.id.desc()).limit(n))
    rows = (await db.execute(stmt)).scalars().all()
    return list(reversed(rows))
    
