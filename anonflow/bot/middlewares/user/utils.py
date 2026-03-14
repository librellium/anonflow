from typing import Optional

from aiogram.types import Message, User


def extract_message(event) -> Optional[Message]:
    if message := getattr(event, "message", None):
        return message
    if callback_query := getattr(event, "callback_query", None):
        return callback_query.message

def extract_user(event) -> Optional[User]:
    if message := getattr(event, "message", None):
        return message.from_user
    if callback_query := getattr(event, "callback_query", None):
        return callback_query.from_user
