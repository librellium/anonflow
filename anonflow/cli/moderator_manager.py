import asyncio
import inspect
from ast import literal_eval
from contextlib import suppress
from typing import Any, Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from anonflow import paths
from anonflow.config import Config
from anonflow.constants import SYSTEM_USER_ID
from anonflow.database import (
    BanRepository,
    Database,
    ModeratorRepository,
)
from anonflow.services import ModeratorService


class ModeratorManager:
    def __init__(self):
        self._allowed_commands = (
            "add", "can", "get",
            "has", "remove", "update",
        )

        self._completer = WordCompleter(self._allowed_commands, ignore_case=True)
        self._session = PromptSession(completer=self._completer)

        self._config = Config.load(paths.CONFIG_FILEPATH)
        self._database = Database(self._config.get_database_url())
        self._service = ModeratorService(
            self._database, BanRepository(), ModeratorRepository()
        )

    @staticmethod
    async def _execute(method, *args, **kwargs):
        try:
            sig = inspect.signature(method)
            if "actor_user_id" in sig.parameters:
                result = await method(SYSTEM_USER_ID, *args, **kwargs)
            else:
                result = await method(*args, **kwargs)
            if result is not None:
                return result
        except Exception as e:
            return str(e)

    @staticmethod
    def _parse_text(text: str):
        text = text.strip()
        if not text:
            return

        command, *raw_args = text.split()

        args: List[Any] = []
        kwargs: Dict[str, Any] = {}

        for arg in raw_args:
            if "=" in arg and all(s := arg.split("=", maxsplit=1)):
                key, value = s[0].strip(), s[1].strip()
                if key != "actor_user_id":
                    with suppress(ValueError):
                        value = literal_eval(value)
                    kwargs[key] = value
            else:
                with suppress(ValueError):
                    arg = literal_eval(arg)
                args.append(arg)

        return command, args, kwargs

    async def close(self):
        await self._database.close()

    async def init(self):
        await self._database.init()

    async def run(self):
        while True:
            try:
                text: str = await self._session.prompt_async("[ModeratorManager]> ")
            except KeyboardInterrupt:
                print("Use CTRL+D or type 'exit' to exit")
                continue
            except EOFError:
                break
            else:
                if parsed := self._parse_text(text):
                    command, args, kwargs = parsed

                    if command in ["exit", "quit", "q"]:
                        break

                    if command in self._allowed_commands and (
                        method := getattr(self._service, command, None)
                    ):
                        result = await self._execute(method, *args, **kwargs)
                        if result is not None:
                            print(result)
                    else:
                        print(f"Unknown command: {command}")


async def main():
    manager = ModeratorManager()
    try:
        await manager.init()
        await manager.run()
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())
