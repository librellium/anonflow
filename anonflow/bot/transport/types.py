from dataclasses import dataclass

from aiogram.types import ChatIdUnion


@dataclass(frozen=True)
class RequestContext:
    chat_id: ChatIdUnion
    user_language: str
