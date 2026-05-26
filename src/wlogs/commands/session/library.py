from pathlib import Path
import os
import sys
import json
from typing import Any
from datetime import datetime
from ...utils.file_lib import list_scenes, get_last_line

# Path to temp file that holds session data while running
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

# Get session data out of temporary file
def load_session_data():
    path = state_path()
    if path.exists():
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {}
    else:
        data = {}
    return data
def session_in_progress():
    if load_session_data():
        return True
    else:
        return False

def remove_session_data(path: Path) -> None:
    if path.exists():
        path.unlink()

def validate_session(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        print("No session in progress.", file=sys.stderr)
        sys.exit(2)
    data["stop_time"] = now_iso()
    if not data["scene_code"] or not data["start_time"]:
        print("State file is missing sceneCode/startTime. Try `wlogs cancel` and start again.", file=sys.stderr)
        sys.exit(2)
    return data

def convert_to_session(file_data: dict[str, Any], words: int):
    session = {
        "date": file_data["date"],
        "startTime": file_data["start_time"],
        "stopTime": now_iso(),
        "words": words,
        "sceneCode": file_data["scene_code"]
    }
    return session

def store_local_session(session, log_name):
    path = list_scenes(log_name)
    columns = get_last_line(path).split(",")
    next_id = int(columns[0]) + 1
    row = f"{next_id},{session["date"]},{session["startTime"]},{session["stopTime"]},{session["sceneCode"]},{session["words"]},"
    with open(path, 'a') as f:
        f.write(row)
    return row

def print_dict(data: dict[str, Any]):
    for key, value in data.items():
        print(f"{key}: {value}")

def now_iso() -> str:
    # ISO-8601 with local offset, seconds precision
    return datetime.now().astimezone().isoformat(timespec="seconds")

def write_json_to_file(path: Path, data: dict[str, Any]):
    with open(path, 'w') as f:
        json.dump(data, f)