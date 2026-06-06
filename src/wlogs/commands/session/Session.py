import sys
import json
from ...config import CONFIG
from ...utils.file_lib import get_last_line


class Session:
    # Path to temp file that holds session data while running
    def __init__(self) -> None:
        self.state_path = CONFIG["state"] / "current_session.json"
        self.data = self.load_session_data()
        self.log = CONFIG["log_path"]

    # Get session data out of temporary file
    def load_session_data(self):
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
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
        if self.data:
            return True
        else:
            return False

    # After saving, remove data from temp file
    def remove_session_data(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()

    def handle_no_data(self):
        if not self.data:
            print("No session in progress.", file=sys.stderr)
            sys.exit(2)
        if not self.data["scene_code"] or not self.data["start_time"]:
            print(
                "State file is missing sceneCode/startTime. Try `wlogs cancel` and start again.",
                file=sys.stderr,
            )
            sys.exit(2)

    def convert_to_session(self):
        session = {
            "date": self.data["date"],
            "startTime": self.data["start_time"],
            "stopTime": self.data["stop_time"],
            "words": self.data["words"],
            "sceneId": self.data["scene_id"]
        }
        return session

    def store_local_session(self):
        columns = get_last_line(self.log).split(",")
        next_id = int(columns[0]) + 1
        row = f"{next_id},{self.data['date']},{self.data['start_time']},{self.data['stop_time']},{self.data['scene_code']},{self.data['words']},\n"
        with open(self.log, "a") as f:
            f.write(row)
        return row


