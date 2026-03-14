from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callbacks import PostCallbackData


class Keyboards:
    @staticmethod
    def get_post_markup(t_kb):
        builder = InlineKeyboardBuilder()

        builder.button(
            text=t_kb("post.approve"),
            callback_data=PostCallbackData(action="approve")
        )
        builder.button(
            text=t_kb("post.reject"),
            callback_data=PostCallbackData(action="reject")
        )

        builder.adjust(2)

        return builder.as_markup()
