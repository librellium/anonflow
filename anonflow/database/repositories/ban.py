from aiogram.types import ChatIdUnion
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from anonflow.database.orm import Ban


class BanRepository:
    async def ban(self, session: AsyncSession, actor_chat_id: ChatIdUnion, chat_id: ChatIdUnion):
        async with session.begin():
            ban = Ban(
                chat_id=chat_id,
                banned_by=actor_chat_id
            )
            session.add(ban)

    async def is_banned(self, session: AsyncSession, chat_id: ChatIdUnion):
        result = await session.execute(
            select(Ban)
            .where(
                Ban.chat_id == chat_id,
                Ban.is_active.is_(True)
            )
            .limit(1)
        )
        return bool(result.scalar_one_or_none())

    async def unban(self, session: AsyncSession, actor_chat_id: ChatIdUnion, chat_id: ChatIdUnion):
        async with session.begin():
            await session.execute(
                update(Ban)
                .where(
                    Ban.chat_id == chat_id,
                    Ban.is_active.is_(True)
                )
                .values(
                    is_active=False,
                    unbanned_at=func.now(),
                    unbanned_by=actor_chat_id
                )
            )
