# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
from __future__ import annotations
import os
from pathlib import Path
LOG_FILE = "master-writing-log"
API_URL = "http://localhost:8081/api"
HOME_DIR = Path(Path.home() / "repos")
def base_url() -> str:
    return os.getenv("WLOGS_BASE_URL", API_URL).rstrip("/")

