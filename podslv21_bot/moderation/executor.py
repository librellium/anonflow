import logging
from typing import AsyncGenerator, Literal

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from yarl import URL

from podslv21_bot.config import Config

from .models import ModerationEvent, ModerationDecision
from .planner import ModerationPlanner


class ModerationExecutor:
    def __init__(self,
                 config: Config,
                 bot: Bot,
                 planner: ModerationPlanner):
        self._logger = logging.getLogger("podslv21_bot.moderation.executor")

        self.config = config
        self.bot = bot

        self.planner = planner
        self.planner.set_functions(self.delete_message, self.moderation_decision)

    async def delete_message(self, message_link: str):
        """
        Deletes a message by message_link.
        Call this function only when the user explicitly requests to delete their own message.
        Do not use it for moderation or automatic cleanup.
        """
        parsed_url = URL(message_link)
        parsed_path = parsed_url.path.strip("/").split("/")

        moderation_chat_id = self.config.forwarding.moderation_chat_id
        publication_chat_id = self.config.forwarding.publication_chat_id

        if len(parsed_path) == 3 and parsed_path[0] == "c"\
            and parsed_path[1].replace("-100", "") == str(publication_chat_id).replace("-100", ""):
                message_id = parsed_path[2]
                try:
                    await self.bot.delete_message(publication_chat_id, message_id)
                    await self.bot.send_message(
                        moderation_chat_id,
                        f"<b>Исполнитель</b>: Удаление успешно для {message_id}.",
                        parse_mode="HTML"
                    )
                    return ModerationEvent(type="delete_message", result=True)
                except TelegramBadRequest:
                    await self.bot.send_message(
                        moderation_chat_id,
                        f"<b>Исполнитель</b>: Удаление окончилось ошибкой для {message_id}.",
                        parse_mode="HTML"
                    )
                    return ModerationEvent(type="delete_message", result=False)

    async def moderation_decision(self, status: Literal["PASS", "REJECT"], explanation: str):
        """
        Processes a message with a moderation decision by status and explanation. 
        This function must be called whenever there is no exact user request or no other available function 
        matching the user's intent. Status must be either "PASS" if the message is allowed, or "REJECT" if it should be blocked.
        """
        moderation_chat_id = self.config.forwarding.moderation_chat_id
        human_status = "отправлено" if status == "PASS" else "отклонено"

        await self.bot.send_message(
            moderation_chat_id,
            f"<b>Исполнитель</b>: Сообщение {human_status}.\n\nОбъяснение: {explanation}",
            parse_mode="HTML"
        )

        if status not in ("PASS", "REJECT"):
            return ModerationEvent(type="moderation_decision", result=ModerationDecision(status="REJECT", explanation=explanation))

        return ModerationEvent(type="moderation_decision", result=ModerationDecision(status=status, explanation=explanation))

    async def process_message(self, message_text: str) -> AsyncGenerator[ModerationEvent, None]:
        functions = await self.planner.plan(message_text)
        function_names = self.planner.get_function_names()

        for func in functions:
            func_name = func.get("name")
            if hasattr(self, func_name) and func_name in function_names:
                try:
                    self._logger.info(f"Executing {func_name}({', '.join(map(str, func.get('args')))})")
                    yield await getattr(self, func_name)(*func.get("args"))
                except Exception:
                    self._logger.exception(f"Failed to execute {func_name}({', '.join(map(str, func.get('args')))})")