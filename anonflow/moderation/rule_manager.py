import logging
from os import listdir
from pathlib import Path
from typing import List


class RuleManager:
    def __init__(self, rules_dir: Path):
        self._logger = logging.getLogger(__name__)

        self._rules_dir = rules_dir
        self._rules: List[str] = []

    def reload(self):
        if not self._rules_dir.exists():
            self._rules_dir.mkdir(parents=True, exist_ok=True)

        self._rules.clear()
        for rule_filename in listdir(self._rules_dir):
            if rule_filename.endswith(".example"):
                continue

            rule_filepath = Path(self._rules_dir / rule_filename).resolve()
            with rule_filepath.open(encoding="utf-8") as rule_file:
                rule = rule_file.read()
                if rule:
                    self._rules.append(rule)

        self._logger.info("Rules loaded. Total=%d", len(self._rules))

    def get_rules(self):
        return self._rules.copy()
