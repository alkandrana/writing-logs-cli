# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
from __future__ import annotations
import os
from pathlib import Path

from wlogs.commands.config import load_config

CONFIG = load_config()

# def base_url() -> str:
#     return os.getenv("WLOGS_BASE_URL", API_URL).rstrip("/")
