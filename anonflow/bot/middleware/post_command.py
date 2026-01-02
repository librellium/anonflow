from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message

from .utils import extract_message


class PostCommandMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event, data):
        message = extract_message(event)

        data["is_post"] = False

        if isinstance(message, Message) and message.chat.type == ChatType.PRIVATE:
            source_text = message.text if message.text is not None else message.caption
            if not source_text:
                return await handler(event, data)

            cmd, *rest = source_text.lstrip().split(maxsplit=1)
            if cmd != "/post":
                return await handler(event, data)

            post_text = rest[0].strip() if rest else ""

            if message.text is not None and not post_text:
                return

            data["is_post"] = True

        return await handler(event, data)
