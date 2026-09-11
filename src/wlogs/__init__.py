import json
import os
import sys
from pathlib import Path


def load_config() -> dict[str, str]:
    config_path = get_store_path() / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config: dict[str, str] = json.load(f)
        if "api_url" not in config or "log_file" not in config or "novel_home" not in config:
            print(
                "Config not complete. Set it up with 'wlogs config log' or 'wlogs config api' or 'wlogs config novel'"
            )
            sys.exit(1)
        return config
    else:
        print("Config could not be found. Set it up with 'wlogs config'.")
        sys.exit(1)


def get_store_path() -> Path:
    # Prefer XDG_STATE_HOME; fallback to ~/.local/state; then ~/.wlogs if needed.
    xdg_state = os.getenv("XDG_STATE_HOME")
    if xdg_state:
        root = Path(xdg_state)
    else:
        root = Path.home() / ".local" / "state"

    path = root / "wlogs"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
