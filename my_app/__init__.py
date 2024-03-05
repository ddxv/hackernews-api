"""Try loading config and umami settings."""

import tomllib
from pathlib import Path

from config import get_logger

logger = get_logger(__name__)

UMAMI_FILENAME = "umami_settings.toml"

try:
    file_path = Path(__file__).parent / UMAMI_FILENAME
except NameError:
    file_path = Path(UMAMI_FILENAME)

UMAMI_SETTINGS = {}
if file_path.exists():
    logger.info(f"loading umami settings from {file_path=}")
    with Path.open(file_path, "rb") as file:
        UMAMI_SETTINGS = tomllib.load(file)
else:
    logger.info(f"unable to find umami settings from {file_path=}")

