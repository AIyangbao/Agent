from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.tags import tag
async def get_tag_list(db: AsyncSession):
    res = await db.execute(select(tag).where(tag.is_delete == False).order_by(tag.id))
    data = [{"id": r.id, "name": r.name} for r in res.scalars().all()]
    return data