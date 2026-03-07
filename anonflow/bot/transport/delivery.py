from typing import Optional, List, Union

from aiogram import Bot
from aiogram.client.bot import Default
from aiogram.types import (
    ChatIdUnion,
    InputMediaPhoto,
    InputMediaVideo,
    MediaUnion,
    ReplyMarkupUnion,
)

from .content import ContentGroup, ContentItem, ContentTextItem, MediaType


class DeliveryService:
    def __init__(self, bot: Bot):
        self._bot = bot

    @staticmethod
    def _wrap_content_item(
        item, parse_mode: Optional[Union[str, Default]] = Default("parse_mode")
    ):
        if item.type == MediaType.PHOTO:
            return InputMediaPhoto(
                media=item.file_id, caption=item.caption, parse_mode=parse_mode
            )
        elif item.type == MediaType.VIDEO:
            return InputMediaVideo(
                media=item.file_id, caption=item.caption, parse_mode=parse_mode
            )
        else:
            raise ValueError("Media item type is invalid.")

    async def delete(self, chat_id: ChatIdUnion, message_id: int):
        return await self._bot.delete_message(chat_id, message_id)

    async def send_content(
        self,
        chat_id: ChatIdUnion,
        content: Union[ContentItem, ContentGroup],
        parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
        reply_markup: Optional[ReplyMarkupUnion] = None,
    ):
        if isinstance(content, ContentTextItem):
            await self.send_text(
                chat_id, content.text, parse_mode=parse_mode, reply_markup=reply_markup
            )
        elif isinstance(content, ContentGroup):
            if len(content) > 1:
                await self.send_media_group(
                    chat_id,
                    [self._wrap_content_item(item, parse_mode) for item in content],
                )
            elif len(content) == 1:
                await self.send_media(
                    chat_id,
                    self._wrap_content_item(content[0]),
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                )

    async def send_media(
        self,
        chat_id: ChatIdUnion,
        media: MediaUnion,
        parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
        reply_markup: Optional[ReplyMarkupUnion] = None,
    ):
        if isinstance(media, InputMediaPhoto):
            return await self._bot.send_photo(
                chat_id,
                media.media,
                caption=media.caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        elif isinstance(media, InputMediaVideo):
            return await self._bot.send_video(
                chat_id,
                media.media,
                caption=media.caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )

    async def send_media_group(
        self,
        chat_id: ChatIdUnion,
        media_group: List[MediaUnion],
    ):
        return await self._bot.send_media_group(chat_id=chat_id, media=media_group)

    async def send_text(
        self,
        chat_id: ChatIdUnion,
        text: str,
        parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
        reply_markup: Optional[ReplyMarkupUnion] = None,
    ):
        return await self._bot.send_message(
            chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup
        )
