from pathlib import Path
import os
import sys
import json
from typing import Any
from ...utils.file_lib import get_last_line, find_files
from ...utils.data_lib import get_current_timestamp


class SessionManager:
    # Path to temp file that holds session data while running
    def __init__(self, log) -> None:
        # Prefer XDG_STATE_HOME; fallback to ~/.local/state; then ~/.wlogs if needed.
        xdg_state = os.getenv("XDG_STATE_HOME")
        if xdg_state:
            root = Path(xdg_state)
        else:
            root = Path.home() / ".local" / "state"

        self.path = root / "wlogs" / "current_session.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.log_file = log

    # Get session data out of temporary file
    def load_session_data(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                code_parts = data["scene_code"].split("-")
                data["project_code"] = code_parts[0]
                data["scene_code"] = code_parts[1]
            except json.decoder.JSONDecodeError:
                data = {}
        else:
            data = {}
        return data

    # Check if data in temp file = previous has not been terminated
    def session_in_progress(self):
        if self.load_session_data():
            return True
        else:
            return False

    # After saving, remove data from temp file
    def remove_session_data(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def handle_no_data(self, data: dict[str, Any]):
        if not data:
            print("No session in progress.", file=sys.stderr)
            sys.exit(2)
        if not data["scene_code"] or not data["start_time"]:
            print(
                "State file is missing sceneCode/startTime. Try `wlogs cancel` and start again.",
                file=sys.stderr,
            )
            sys.exit(2)

    def convert_to_session(self, file_data: dict[str, Any], words: int):
        session = {
            "date": file_data["date"],
            "startTime": file_data["start_time"],
            "stopTime": get_current_timestamp(),
            "words": words,
            "sceneCode": file_data["scene_code"],
        }
        return session

    def store_local_session(self, session):
        path = find_files(self.log_file)
        columns = get_last_line(path).split(",")
        next_id = int(columns[0]) + 1
        row = f"{next_id},{session['date']},{session['startTime']},{session['stopTime']},{session['sceneCode']},{session['words']},\n"
        with open(path, "a") as f:
            f.write(row)
        return row

    def get_scene_id(self, scene_code: str, api) -> int|None:
        scene = api.get_results(scene_code, "scenes/code")
        if scene:
            return scene["id"]
        else:
            print(f"No scene with code {scene_code} found. Create it with 'wlogs scene new'", file=sys.stderr)
            sys.exit(1)

    def get_project_id(self, code, api) -> int:
        project = api.get_one_record(code, "projects/code")
        if project:
            return project["id"]
        else:
            print(f"No project with code {code} found. Create it with 'wlogs project new'", file=sys.stderr)
            sys.exit(1)
