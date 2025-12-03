import inspect
import json
import logging
from json import JSONDecodeError
from typing import Dict, List, Union

from openai import APIResponseValidationError, AsyncOpenAI

from podslv21_bot.config import Config

from .rule_manager import RuleManager


class ModerationPlanner:
    def __init__(self,
                 config: Config,
                 rule_manager: RuleManager):
        self._logger = logging.getLogger(__name__)

        self.config = config
        self.rule_manager = rule_manager

        self._client = AsyncOpenAI(api_key=self.config.openai.api_key.get_secret_value(),
                                   timeout=self.config.openai.timeout,
                                   max_retries=self.config.openai.max_retries)
        self.moderation = self.config.moderation.enabled

        self._functions: List[Dict[str]] = []

    def set_functions(self, *functions):
        if not functions:
            return

        self._functions.clear()
        for func in functions:
            sig = inspect.signature(func)
            args = {name: str(param.annotation) if param.annotation != inspect._empty else "str"
                    for name, param in sig.parameters.items()}

            self._functions.append({
                "name": func.__name__,
                "args": args,
                "description": func.__doc__ or ""
            })

        self._logger.info(f"Functions added: {', '.join(self.get_function_names())}. Total={len(self._functions)}")

    def get_function_names(self) -> Union[List[str], None]:
        return [f.get("name") for f in self._functions]

    async def plan(self, message_text: str) -> List[Dict[str, Union[list, str]]]:
        mod_response = await self._client.moderations.create(
            model="omni-moderation-latest",
            input=[
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        )

        funcs = self._functions
        funcs_prompt = "\n".join(
            f"- {func['name']}({', '.join(f'{arg}: {ann}' for arg, ann in (func.get('args') or {}).items())})"
            f" - {func.get('description', '')}"
            for func in funcs
        )

        retry = 0
        result = None

        while retry <= self._client.max_retries:
            response = await self._client.responses.create(
                model=self.config.moderation.model,
                input=[
                    {
                        "role": "system",
                        "content": "Ответь строго JSON-массивом вида:\n"
                                   '`[{"name": ..., "args": [...]}, ...]`\n'
                                   "`name` - название функции, `args` - последовательность аргументов.\n"
                                   "Выведи только подходящий JSON, выбирай функции в "
                                   "соответствии с запросом пользователя и описанием функции "
                                   "Ты в праве вызывать несколько функций, указывая их по порядку в выводе.\n\n"
                                   "**ВАЖНО:**\n"
                                   "- Каждая функция должна содержать **все и только обязательные аргументы**, указанные в её описании.\n"
                                   "- Не придумывай дополнительных аргументов.\n"
                                   "- Не пропускай обязательные аргументы.\n"
                                   "- `args` должны быть в том порядке, который указан в описании функции.\n\n"
                                   "Доступные функции:\n"
                                   f"{funcs_prompt}"
                    },
                    *[{"role": "system", "content": rule} for rule in self.rule_manager.get_rules()],
                    {
                        "role": "user",
                        "content": message_text
                    }
                ]
            )

            try:
                text = response.output_text

                start = text.index("[")
                end = text.rindex("]") + 1

                result = json.loads(text[start:end])
                break
            except JSONDecodeError:
                retry += 1

        if not result:
            raise APIResponseValidationError()

        return result