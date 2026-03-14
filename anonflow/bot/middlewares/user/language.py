from aiogram import BaseMiddleware

from .utils import extract_user


class UserLanguageMiddleware(BaseMiddleware):
    def __init__(self, fallback_language: str):
        super().__init__()

        self._fallback_language = fallback_language

    async def __call__(self, handler, event, data):
        data["user_language"] = self._fallback_language

        from_user = extract_user(event)
        if from_user:
            user = data.get("user")
            data["user_language"] = (
                user.language if user else from_user.language_code
            )

        return await handler(event, data)
