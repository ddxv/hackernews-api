"""Try loading umami settings."""

import tomllib
from pathlib import Path

filename = "umami_settings.toml"

try:
    file_path = Path(__file__).parent / filename
except NameError:
    file_path = Path(filename)

UMAMI_SETTINGS = {}
if file_path.exists():
    with Path.open(file_path, "rb") as file:
        UMAMI_SETTINGS = tomllib.load(file)
