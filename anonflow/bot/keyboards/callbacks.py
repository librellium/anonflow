from typing import Literal

from aiogram.filters.callback_data import CallbackData


class PostCallbackData(CallbackData, prefix="post"):
    action: Literal["approve", "reject"]