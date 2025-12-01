import asyncio
import logging

from aiogram import Bot, Dispatcher

from podslv21_bot.bot import MessageManager, build
from podslv21_bot.config import Config
from podslv21_bot.moderation import (ModerationExecutor,
                                     ModerationPlanner,
                                     RuleManager)

from . import paths


async def main():
    if not paths.CONFIG_FILE.exists():
        Config().save(paths.CONFIG_FILE)

    config = Config.load(paths.CONFIG_FILE)

    logging.basicConfig(format=config.logging.fmt,
                        datefmt=config.logging.date_fmt,
                        level=config.logging.level)

    bot = Bot(token=config.bot.token.get_secret_value())
    dispatcher = Dispatcher()

    message_manager = MessageManager()

    executor = None
    if config.moderation.enabled:
        rule_manager = RuleManager(paths.RULES_DIR)
        rule_manager.reload()
        planner = ModerationPlanner(config, rule_manager)
        executor = ModerationExecutor(config, bot, planner)

    dispatcher.include_router(
        build(config, message_manager, executor)
    )

    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())