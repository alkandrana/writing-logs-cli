import csv
from datetime import datetime
from pathlib import Path
from .. import get_store_path, load_config
from ..library.dates import to_zulu, print_dict
from ..library.api.sessions.create_session import post_session
from ..library.api.scenes.scene import get_scene_id
import sys, os, json

from ..library.file.search import find_file


def initialize(scene):
    session_data = {
        "date": datetime.strftime(datetime.today(), "%Y-%m-%d"),
        "start_time": datetime.isoformat(datetime.now().astimezone()),
        "scene": scene,
    }
    return session_data


def tmp_save(data):
    path = get_store_path() / "session.json"
    if path.exists():
        print(f"Session already running.")
        sys.exit(1)
    else:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)


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


def get_next_id():
    path = Path(load_config()['log_file'])
    if path.exists():
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                id = int(row["session_id"])
        return id + 1
    else:
        print("Log file not found.")
        sys.exit(1)


def save_local(data):
    path = Path(load_config()['log_file'])
    id = get_next_id()
    csv_str = f"{id},{data['date']},{data['start_time']},{data['stop_time']},{data['scene']},{data['words']},{data['comments'] if 'comments' in data else ""}\n"
    if path.exists():
        with open(path, "a") as f:
            f.write(csv_str)
        print(f"Session saved to {path}")
    else:
        print("Log file not found.")
        sys.exit(1)


def convert_to_session(data):
    print(data)
    scene_id = get_scene_id(data["scene"])
    return {
        "date": data["date"],
        "startTime": to_zulu(data["start_time"]) if data["start_time"] else data["start_time"],
        "stopTime": to_zulu(data["stop_time"]) if data["stop_time"] else data["stop_time"],
        "words": data["words"],
        "sceneId": scene_id,
    }


def start(args):
    data = initialize(args.scene)
    tmp_save(data)
    print("Session started: ")
    for key, value in data.items():
        print(f"{key}: {value}")


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

def novelwrite_session(args):
    project = input("Project Name: ")
    path = find_file(project, full_name=True)
    if not path.exists():
        print("Project folder could not be located. Check spelling and try again.")
        sys.exit(1)
    else:
        session_json = path / "meta" / "sessions.jsonl"
        with open(session_json, "r") as f:
            for line in f:
                session = line.strip()
        ses_dict = json.loads(session)
        start = datetime.fromisoformat(ses_dict["start"]).astimezone() if "start" in ses_dict else None
        stop = datetime.fromisoformat(ses_dict["end"]).astimezone() if "end" in ses_dict else None
        session = {
            "date": datetime.strftime(start, "%Y-%m-%d"),
            "start_time": to_zulu(start.isoformat()) if start else None,
            "stop_time": to_zulu(stop.isoformat()) if stop else None,
            "words": args.words,
            "scene": args.scene,
        }

def status(_):
    path = get_store_path() / "session.json"
    if not path.exists():
        print("No session currently running.")
    else:
        with open(path, "r") as f:
            data = json.load(f)
        print("Current session: ")
        print_dict(data)


def cancel(_):
    path = get_store_path() / "session.json"
    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
        path.unlink()
        print("Session cancelled: ")
        for key, value in data.items():
            print(f"{key}: {value}")
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
