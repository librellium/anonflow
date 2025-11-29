from aiogram import Router

from simpleforward.config import Config

from .message_manager import MessageManager
from .routers.photo import PhotoRouter
from .routers.start import StartRouter
from .routers.text import TextRouter


def build(config: Config, message_manager: MessageManager):
    main_router = Router()

    main_router.include_routers(
        StartRouter(),
        TextRouter(
            config, message_manager
        ),
        PhotoRouter(
            config, message_manager
        )
    )

    return main_router