import csv
import sys, json
from datetime import datetime, date
from pathlib import Path
from ..library.api.sessions.create_session import post_session
from .. import get_store_path, load_config
from ..library.dates import to_zulu, print_dict
from ..library.api.scenes.scene import get_scene_id
from ..library.file.search import find_file

# Construct dict of starting session data
def initialize(scene):
    session_data = {
        "date": datetime.now().astimezone().date(),
        "start_time": datetime.isoformat(datetime.now().astimezone()),
        "scene": scene,
    }
    return session_data

# save start data to temp file
def tmp_save(data):
    path = get_store_path() / "session.json"
    if path.exists():
        print("Session already running.")
        sys.exit(1)
    else:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

# construct final session dict (after session completion)
def build_session(words):
    path = get_store_path() / "session.json"
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
        if not "stop_time" in data:
            data["stop_time"] = datetime.isoformat(datetime.now().astimezone())
        data["words"] = words
    else:
        print("No session running.")
        sys.exit(1)
    return data

# calculate new id for session for local file
def get_next_id():
    path = Path(load_config()['log_file'])
    if path.exists():
        session_id = 0
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                session_id = int(row["session_id"])
        return session_id + 1
    else:
        print("Log file not found.")
        sys.exit(1)

# save constructed session to local file
def save_local(data):
    path = Path(load_config()['log_file'])
    session_id = get_next_id()
    csv_str = f"{session_id},{data['date']},{data.get('start_time', '')},{data.get('stop_time', '')},{data['scene']},{data['words']},{data.get('comments', '')}\n"
    if path.exists():
        with open(path, "a") as f:
            f.write(csv_str)
        print(f"Session saved to {path}")
    else:
        print("Log file not found.")
        sys.exit(1)

# format constructed session as payload to send to API
def convert_to_session(data):
    print(f"Local session: {data}")
    scene_id = get_scene_id(data["scene"])
    return {
        "date": data["date"],
        "startTime": to_zulu(data["start_time"]) if data["start_time"] else data["start_time"],
        "stopTime": to_zulu(data["stop_time"]) if data["stop_time"] else data["stop_time"],
        "words": data["words"],
        "sceneId": scene_id,
    }

# start session command
def start(args):
    data = initialize(args.scene)
    tmp_save(data)
    print("Session started: ")
    for key, value in data.items():
        print(f"{key}: {value}")

# stop session command
def stop(args):
    data = build_session(args.words)
    print("Session to save: ", data)
    session = convert_to_session(data)
    status = post_session(session)
    if 200 <= status.status_code < 300:
        save_local(data)
        path = get_store_path() / "session.json"
        path.unlink(missing_ok=True)
        print("Session saved")
    else:
        print("Unable to save session to API.")

# save session (retroactively) command
def save(args):
    # scene_id = get_scene_id(args.scene)
    data = {
        "date": args.date,
        "start_time": args.start_time if args.start_time else None,
        "stop_time": args.stop_time if args.stop_time else None,
        "words": args.words,
        "scene": args.scene,
        "comments": args.comments if args.comments else None
    }
    session = convert_to_session(data)
    print("Session to save: ", session)
    res = post_session(session)
    if 200 <= res.status_code < 300:
        save_local(data)
        print("Session saved")

# experiment: get session details from Novelwriter session json file for saving to the api/local file
def novelwrite_session(args):
    project = input("Project Name: ")
    path = find_file(project, full_name=True)
    if not path or not path.exists():
        print("Project folder could not be located. Check spelling and try again.")
        sys.exit(1)
    else:
        session_json = path / "meta" / "sessions.jsonl"
        session = ""
        with open(session_json, "r") as f:
            for line in f:
                session = line.strip()
        if session:
            ses_dict = json.loads(session)
        else:
            print("Error: No sessions found in file.")
            sys.exit(1)
        start = datetime.fromisoformat(ses_dict["start"]).astimezone() if "start" in ses_dict else None
        stop = datetime.fromisoformat(ses_dict["end"]).astimezone() if "end" in ses_dict else None
        session = {
            "date": datetime.strftime(start, "%Y-%m-%d") if start else datetime.now().astimezone().date(),
            "start_time": to_zulu(start.isoformat()) if start else None,
            "stop_time": to_zulu(stop.isoformat()) if stop else None,
            "words": args.words,
            "scene": args.scene,
        }

# check details for current session (command)
def status(_):
    path = get_store_path() / "session.json"
    if not path.exists():
        print("No session currently running.")
    else:
        with open(path, "r") as f:
            data = json.load(f)
        print("Current session: ")
        print_dict(data)

# cancel current session (command)
def cancel(_):
    path = get_store_path() / "session.json"
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
        path.unlink()
        print("Session cancelled: ")
        print_dict(data)
    else:
        print("No session running.")


def parse_session(subparsers):
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers(dest="subcommand")

    start_parser = session_subparsers.add_parser("start")
    start_parser.add_argument("--scene", "-s", help="Scene Code")
    start_parser.set_defaults(func=start)

    stop_parser = session_subparsers.add_parser("stop")
    stop_parser.add_argument("--words", "-w", help="Words Written")
    stop_parser.set_defaults(func=stop)

    save_parser = session_subparsers.add_parser("save")
    save_parser.add_argument("--scene", "-s", required=True, help="Scene Code")
    save_parser.add_argument("--date", "-d", required=True, help="Session Date")
    save_parser.add_argument("--words", "-w", required=True, help="Words Written")
    save_parser.add_argument("--start_time", "-b", required=False, help="Session Start Time")
    save_parser.add_argument("--stop_time", "-e", required=False, help="Session End Time")
    save_parser.add_argument("--comments", "-c", required=False, help="Session Comments")
    save_parser.set_defaults(func=save)

    status_parser = session_subparsers.add_parser("status")
    status_parser.set_defaults(func=status)

    cancel_parser = session_subparsers.add_parser("cancel")
    cancel_parser.set_defaults(func=cancel)
