from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.musics import Music
from schemas.musics import MusicResponse

async def get_music_list(db: AsyncSession):
    query = select(Music).order_by(Music.id.desc())
    result = await db.execute(query)
    rows = result.scalars().all()
    return [MusicResponse.model_validate(r) for r in rows]