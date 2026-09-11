import os, sys, json
from typing import Any
from pathlib import Path
from datetime import datetime, timezone
from dateutil import parser
from wlogs.commands.setup.config import get_store_path


def to_zulu(date_str: str) -> str:
    date = datetime.fromisoformat(date_str) # expects ISO string with local offset
    dtu = date.astimezone(timezone.utc) # converts local to utc
    return dtu.strftime("%Y-%m-%dT%H:%M:%SZ")


def to_local(date_str):
    iso = datetime.fromisoformat(date_str)
    return str(iso.astimezone())

def normalize_date(date_str: str) -> str:
    date = parser.parse(date_str)
    utc_date = date.astimezone(timezone.utc)
    local_date = utc_date.astimezone()
    return local_date.isoformat()

def format_dates(dates: dict[str, str]):
    valid_dates = {}
    for key, value in dates.items():
        try:
            date = datetime.fromisoformat(value)
            valid_dates[key] = date
        except ValueError:
            print(
                f"Date {value} is not a valid date. "
                f"Please check your date inputs for valid ISO formatting: YYYY-MM-DD HH:MM:SS"
            )
            sys.exit(1)
    if valid_dates["stop"] < valid_dates["start"]:
        print(
            f"Stop date {valid_dates['stop']} cannot be earlier than start date {valid_dates['start']}"
        )
        sys.exit(1)


def join_date(time: str, date: str):
    timestamp = time
    if time and len(time.split("T")) < 2 and len(time.split(" ")) < 2:
        timestamp = f"{date}T{time}"
    return timestamp


def print_list(lst: list[Any]):
    for it in lst:
        print(it)


def print_dict(map: dict[str, Any]):
    for key, value in map.items():
        print(f"\n{key}: {value}")

def print_list_dict(lst):
    print("\n")
    for item in lst:
        for key, value in item.items():
            print(f"{key}: {value}")
        print("\n")

def load_json(path: Path):
    if path.exists():
        with open(path, "r", encoding='utf-8-sig') as f:
            data = json.load(f)
    else:
        data = {}
    return data
