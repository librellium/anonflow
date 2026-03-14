from aiogram import BaseMiddleware

from anonflow.services import UserService

from .utils import extract_user


class UserContextMiddleware(BaseMiddleware):
    def __init__(self, user_service: UserService):
        super().__init__()

        self._user_service = user_service

    async def __call__(self, handler, event, data):
        data["user"] = None

        from_user = extract_user(event)
        if from_user:
            data["user"] = await self._user_service.get(from_user.id)

        return await handler(event, data)
