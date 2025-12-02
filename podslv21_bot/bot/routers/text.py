from typing import Optional

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message

from podslv21_bot.bot.message_manager import MessageManager
from podslv21_bot.config import Config
from podslv21_bot.moderation import ModerationExecutor


class TextRouter(Router):
    def __init__(self,
                 config: Config,
                 message_manager: MessageManager,
                 executor: Optional[ModerationExecutor] = None):
        super().__init__()

        self.config = config
        self.message_manager = message_manager
        self.executor = executor

        self._register_handlers()

    def _register_handlers(self):
        @self.message(F.text)
        async def on_text(message: Message, bot: Bot):
            reply_to_message = message.reply_to_message

            if message.chat.id == self.config.forwarding.moderation_chat_id\
                and reply_to_message and reply_to_message.from_user.is_bot:
                    result = self.message_manager.get(reply_to_message.message_id)

                    if result:
                        reply_to_message_id, chat_id = result
                        try:
                            await bot.send_message(chat_id, message.text, reply_to_message_id=reply_to_message_id)
                            await message.answer("Ответ успешно отправлен!")
                        except (TelegramBadRequest, TelegramForbiddenError) as e:
                            await message.answer(f'Не удалось отправить ответ: "{e}"')
            elif message.chat.type == ChatType.PRIVATE and "text" in self.config.forwarding.types:
                try:
                    group_message_id = None
                    targets = {
                        self.config.forwarding.moderation_chat_id: True
                    }

                    moderation_passed = False
                    if self.config.moderation.enabled:
                        sent_message = await message.answer("Сообщение отправлено на модерацию...")
                        async for event in self.executor.process_message(message.text):
                            if event.type == "moderation_decision":
                                if event.result.status == "PASS":
                                    moderation_passed = True
                                elif event.result.status == "REJECT":
                                    await message.answer("Сообщение не прошло модерацию.")

                        await sent_message.delete()
                    else:
                        moderation_passed = True

                    if moderation_passed:
                        targets[self.config.forwarding.publication_chat_id] = False

                    for target, save_message_id in targets.items():
                        reply_to_message_id = message.message_id
                        msg = await bot.send_message(
                            target,
                            self.config.forwarding.message_template.format(text=message.text),
                            parse_mode="HTML"
                        )

                        if save_message_id:
                            group_message_id = msg.message_id

                    self.message_manager.add(reply_to_message_id, group_message_id, message.chat.id)
                    if moderation_passed:
                        await message.answer("Сообщение успешно отправлено!")
                except (TelegramBadRequest, TelegramForbiddenError) as e:
                    await message.answer(f'Не удалось отправить сообщение: "{e}"')