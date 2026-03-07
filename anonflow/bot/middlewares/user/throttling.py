import asyncio
import time
from typing import Dict, Iterable, Optional

from aiogram import BaseMiddleware
from aiogram.types import ChatIdUnion, Message

from anonflow.bot.transport.types import RequestContext
from anonflow.interfaces import UserResponsesPort


class UserThrottlingMiddleware(BaseMiddleware):
    def __init__(
        self,
        responses_port: UserResponsesPort,
        delay: float,
        allowed_chat_ids: Optional[Iterable[ChatIdUnion]] = None,
    ):
        super().__init__()

        self._responses_port = responses_port
        self._delay = delay
        self._allowed_chat_ids = allowed_chat_ids

        self._user_times: Dict[int, float] = {}
        self._user_locks: Dict[int, asyncio.Lock] = {}

        self._lock = asyncio.Lock()

    async def __call__(self, handler, event, data):
        message = getattr(event, "message", None)
        if isinstance(message, Message) and (
            self._allowed_chat_ids is not None
            and message.chat.id not in self._allowed_chat_ids
        ):
            text = message.text or message.caption or ""
            if not text.startswith("/"):
                async with self._lock:
                    user_lock = self._user_locks.setdefault(
                        message.chat.id, asyncio.Lock()
                    )

                if user_lock.locked():
                    start_time = self._user_times.get(message.chat.id) or 0
                    current_time = time.monotonic()

                    await self._responses_port.user_throttled(
                        RequestContext(message.chat.id, data["user_language"]),
                        remaining_time=(
                            round(self._delay - (current_time - start_time))
                            if start_time
                            else 0
                        ),
                    )
                    return

                async with user_lock:
                    start_time = time.monotonic()
                    self._user_times[message.chat.id] = start_time

                    result = await handler(event, data)

                    elapsed_time = time.monotonic() - start_time
                    await asyncio.sleep(max(0, self._delay - elapsed_time))

                async with self._lock:
                    self._user_locks.pop(message.chat.id)

                return result

        return await handler(event, data)
