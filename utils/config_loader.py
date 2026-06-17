from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict[str, Any]:
    file_path = ROOT_DIR / relative_path
    with file_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data or {}
