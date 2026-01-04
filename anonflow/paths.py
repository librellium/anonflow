from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_FILEPATH = ROOT_DIR / "config.yml"
CONFIG_EXAMPLE_FILEPATH = ROOT_DIR / "config.yml.example"

DATABASE_FILEPATH = ROOT_DIR / "anonflow.db"

RULES_DIR = ROOT_DIR / "rules"

TRANSLATIONS_DIR = ROOT_DIR / "translations"
