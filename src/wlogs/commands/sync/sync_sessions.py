import argparse
import csv
import sys
from pathlib import Path

from wlogs import load_config
from wlogs.utils.basic_utils import join_date, to_zulu
from wlogs.utils.crud import get_all_records, get_record_id, post_record


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
def format_local_session(
    ses: dict[str, str | int | None], scene_repo: list[dict[str, str | int]]
):
    scene_id = next(
        sc.get("id")
        for sc in scene_repo
        if str(sc.get("code")).lower() == str(ses["scene"]).lower()
    )
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


def check_sync_sessions(local_sessions: list[dict[str, str | int]]):
    remote_sessions = get_all_records("sessions")
    sessions_to_add = []
    for ses in local_sessions:
        if not any(
            s for s in remote_sessions if s["code"].lower() == str(ses["id"]).lower()
        ):
            sessions_to_add.append(ses)
    return sessions_to_add


def batch_sessions(_: argparse.Namespace):
    print("Getting sessions from file...")
    sessions = get_records_from_csv(load_config()["log_file"])
    print("Checking for sessions that need to be synced...")
    sessions_to_add = check_sync_sessions(sessions)
    print(f"Converting {len(sessions_to_add)} sessions to payload...")
    scene_repo = get_all_records("scenes")
    batch = [format_local_session(s, scene_repo) for s in sessions_to_add]
    print(f"Found {len(batch)} sessions")
    if len(batch) > 0:
        print(f"Example payload: {batch[0]}")
        choice = input("Proceed? (y/n): ")
        if choice.lower() == "y":
            for p in batch:
                post_record(p, "sessions")
    else:
        print("All sessions up to date.")


def parse_batch_sessions(sync_subparsers):
    session_parser = sync_subparsers.add_parser("sessions")
    session_parser.set_defaults(func=batch_sessions)
