import asyncio
import gettext
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Optional


class Translator:
    def __init__(self, translations_dir: Path):
        self._translations_dir = translations_dir

    @staticmethod
    @lru_cache
    def _get_translation(lang: str, domain: str, translations_dir: Path):
        translation = gettext.translation(
            domain, translations_dir, languages=[lang], fallback=True
        )
        return translation

    @staticmethod
    def _format(s: str, **context):
        return s.format_map(defaultdict(str, context))

    async def get(self, lang: str = "ru", domain: str = "messages"):
        translator = await asyncio.to_thread(
            self._get_translation, lang, domain, self._translations_dir
        )

        def _(
            msgid1: str,
            msgid2: Optional[str] = None,
            n: Optional[int] = None,
            **context,
        ):
            return self._format(
                (
                    translator.ngettext(
                        msgid1, msgid2 if msgid2 is not None else msgid1, n
                    )
                    if n is not None
                    else translator.gettext(msgid1)
                ),
                **context,
            )

        return _
