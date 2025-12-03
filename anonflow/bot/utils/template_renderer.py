import logging
from pathlib import Path

from aiogram.types import Message
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class TemplateRenderer:
    def __init__(self, templates_path: Path):
        self._logger = logging.getLogger(__name__)

        self._env = Environment(
            loader=FileSystemLoader(templates_path),
            enable_async=True
        )

    async def _get_context(self, message: Message):
        return {
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username
        }

    async def render(self, template_name: str, message: Message):
        try:
            template = self._env.get_template(template_name)
            context = await self._get_context(message)

            return await template.render_async(**context)
        except TemplateNotFound:
            self._logger.warning(f"Template {template_name} not found.")
            return f"Шаблон не найден для {template_name}"