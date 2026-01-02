from aiogram.types import Message

def strip_post_command(message: Message):
    text = message.text or message.caption or ""

    if not text:
        return message

    cmd, *rest = text.lstrip().split(maxsplit=1)
    if cmd.lower() == "/post":
        to_update = {}
        normalized = " ".join(rest)

        if message.caption:
            to_update["caption"] = normalized
        if message.text:
            to_update["text"] = normalized

        return message.model_copy(update=to_update)

    return message
