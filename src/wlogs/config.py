# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
from __future__ import annotations
import os
from pathlib import Path
import argparse

API_URL = "http://localhost:8081"
HOME_DIR = Path.home()
def base_url() -> str:
    return os.getenv("WLOGS_BASE_URL", API_URL).rstrip("/")

def state_path() -> Path:
    # Prefer XDG_STATE_HOME; fallback to ~/.local/state; then ~/.wlogs if needed.
    xdg_state = os.getenv("XDG_STATE_HOME")
    if xdg_state:
        root = Path(xdg_state)
    else:
        root = Path.home() / ".local" / "state"

    path = root / "wlogs" / "current_session.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='wlogs')
    return parser