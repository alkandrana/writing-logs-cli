import argparse
import csv
import sys
from pathlib import Path

from wlogs import load_config
from wlogs.utils.basic_utils import join_date, to_zulu
from wlogs.utils.crud import get_record_id, post_record


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
def format_local_session(ses: dict[str, str | int | None]):
    scene_id = get_record_id(str(ses["scene"]), "scenes")
    ses["start_time"] = join_date(str(ses["start_time"]), str(ses["date"]))
    ses["stop_time"] = join_date(str(ses["stop_time"]), str(ses["date"]))
    session = {
        "code": ses["id"],
        "date": ses["date"],
        "startTime": to_zulu(ses["start_time"]) if ses["start_time"] else None,
        "stopTime": to_zulu(ses["stop_time"]) if ses["stop_time"] else None,
        "words": ses["words"],
        "sceneId": scene_id,
        "type": ses["type"],
        "comments": ses["comments"],
    }
    return session


def batch_sessions(_: argparse.Namespace):
    print("Getting sessions from file...")
    sessions = get_records_from_csv(load_config()["log_file"])
    print("Converting sessions to payload...")
    batch = [format_local_session(s) for s in sessions]
    print(f"Found {len(batch)} sessions")
    if len(batch) > 0:
        print(f"Example payload: {batch[0]}")
        choice = input("Proceed? (y/n:)")
        if choice.lower() == "y":
            for p in batch:
                post_record(p, "sessions")
    else:
        print("All sessions up to date.")


def parse_batch_sessions(sync_subparsers):
    session_parser = sync_subparsers.add_parser("sessions")
    session_parser.set_defaults(func=batch_sessions)
