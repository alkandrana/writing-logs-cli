import sys
import csv
import argparse
from pathlib import Path

from wlogs import load_config
from wlogs.library.api.batch_post.utils import transfer, batch_from_file
from wlogs.library.api.crud import post_record
from wlogs.library.api.scenes.scene import get_one_scene
from wlogs.library.dates import to_zulu, join_date

# 1. get sessions from log
def get_records_from_csv(path: str):
    if Path(path).exists():
        with open(path) as f:
            reader = csv.DictReader(f)
            records = [row for row in reader]
        print(f"Retrieved {len(records)} records from {path}")
        return records
    else:
        print("Could not find file.")
        sys.exit(1)
# 2. format sessions, accounting for variations in data
def format_local_session(ses: dict[str, str | int]):
    print("Fetching current scene ID:")
    scene_id = get_scene_id(str(ses["scene_id"]))
    ses["start"] = join_date(str(ses["start"]), str(ses["date"]))
    ses["stop"] = join_date(str(ses["stop"]), str(ses["date"]))
    session = {
        "date": ses["date"],
        "startTime": to_zulu(ses["start"]) if ses["start"] else None,
        "stopTime": to_zulu(ses["stop"]) if ses["stop"] else None,
        "words": ses["words"],
        "sceneId": scene_id,
        "comments": ses["note"],
    }
    return session

def get_scene_id(code: str) -> str | int:
    scene = get_one_scene(code)[0]
    scene_id = scene["id"]
    return scene_id

def batch_sessions(_: argparse.Namespace):
    sessions = get_records_from_csv(load_config()['log_file'])
    batch = [format_local_session(s) for s in sessions]
    for p in batch:
        post_record(p, "sessions")

def parse_batch_sessions(sync_subparsers):
    session_parser = sync_subparsers.add_parser("sessions")
    session_parser.set_defaults(func=batch_sessions)

