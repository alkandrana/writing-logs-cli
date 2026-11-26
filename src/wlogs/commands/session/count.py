import sys
from datetime import datetime, timedelta

import pandas as pd

from wlogs import load_config
from wlogs.commands.auth import send_auth_request
from wlogs.utils.basic_utils import to_local
from wlogs.utils.crud import get_record_by_id

pd.set_option("display.max_rows", 100)


def get_all_sessions():
    request = {"method": "GET", "endpoint": f"{load_config()['api_url']}/sessions"}
    res = send_auth_request(request)
    sessions = res.json()
    sessions.sort(key=lambda x: datetime.fromisoformat(x["date"]))
    return sessions


def print_sessions(sessions):
    print(f"\n{len(sessions)} sessions match the criteria:\n")
    if len(sessions) > 50:
        choice = input(f"List all {len(sessions)} sessions? (y/n): ")
        if choice.lower() == "n":
            sys.exit(0)
    sessions = [
        {
            "code": ses["code"] if ses.get("code") else "",
            "date": ses["date"],
            "start": to_local(ses["startTime"]) if ses["startTime"] else "",
            "stop": to_local(ses["stopTime"]) if ses["stopTime"] else "",
            "words": ses["words"],
            "scene": ses["scene"]["code"],
            "duration": round(ses["duration"]) if ses["duration"] else "",
            "wpm": round(ses["wpm"]) if ses["wpm"] else "",
            "type": ses["type"],
        }
        for ses in sessions
    ]
    dataframe = pd.DataFrame(sessions)
    print(dataframe)


def build_session_title(session):
    project = get_record_by_id(session["scene"]["projectId"], "projects")["code"]
    scene = session["scene"]["code"]
    date = session["date"]
    duration = round(session["duration"]) if session["duration"] else 0
    title = f"{duration} minute session in {project} {scene} on {date}"
    return title


def get_writing_days(sessions):
    month_data = [ses for ses in sessions if ses["date"].startswith("2026-11")]
    writing_days = list({datetime.fromisoformat(ses["date"]).day for ses in month_data})
    return writing_days


def get_off_days(args):
    sessions = [ses for ses in get_all_sessions() if ses["date"].startswith("2026-11")]
    days = list({datetime.fromisoformat(ses["date"]).date() for ses in sessions})
    days.sort()
    streaks = [0]
    off_days = 0
    for i in range(len(days)):
        today = days[i]
        if i + 1 < len(days):
            tomorrow = days[i + 1]
        else:
            tomorrow = datetime.now().date()
        streaks[-1] += 1
        if (tomorrow - today).days > 1:
            off_days += (tomorrow - today).days - 1
            streaks.append(0)
        print(
            f"Index: {i} | Today: {today} | Tomorrow: {tomorrow} | Off Days: {off_days}"
        )
    print(f"\nStreaks: {streaks}\nDays taken off: {off_days}\n")


def get_by_date(date, sessions):
    filtered = [s for s in sessions if s["date"].startswith(date)]
    return filtered


def get_by_scene(sessions, scene):
    sessions = [s for s in sessions if s["scene"]["code"] == scene]
    return sessions


def get_by_project(sessions, project):
    sessions = [s for s in sessions if s["scene"]["project"]["code"] == project]
    return sessions


def get_by_type(sessions, type_filter):
    sessions = [s for s in sessions if s["type"] in type_filter]
    return sessions


def count_sessions(sessions):
    count = 0
    for ses in sessions:
        count += ses["words"]
    return count


def calc_wpm(session):
    if not session["startTime"] or not session["stopTime"]:
        print("Wpm cannot be calculated: missing time data")
        sys.exit(1)
    words = session["words"]
    start = datetime.fromisoformat(session["startTime"])
    stop = datetime.fromisoformat(session["stopTime"])
    duration = (stop - start).total_seconds() / 60
    return round(words / duration, 2)


def list_sessions(args):
    sessions = get_all_sessions()
    if len(sys.argv) == 1:
        print(
            "No valid filter found. If you want to see data for all sessions, use 'wlogs session count -a/--all'"
        )
        sys.exit(1)
    if args.scene:
        sessions = get_by_scene(sessions, args.scene)
    if args.project:
        sessions = get_by_project(sessions, args.project)
    if args.date:
        sessions = get_by_date(args.date, sessions)
    if args.today:
        date = datetime.strftime(datetime.today(), "%Y-%m-%d")
        sessions = get_by_date(date, sessions)
    if args.type:
        sessions = get_by_type(sessions, args.type)
    if args.all:
        print(f"WARNING: Found {len(sessions)} sessions in the database.")
        choice = input("Proceed? (y/n): ")
        if choice.lower() == "n":
            sys.exit(0)
    if args.count:
        word_count = count_sessions(sessions)
        print(f"\n{word_count:,} words written in all sessions.")
        sys.exit(0)

    print_sessions(sessions)


def parse_count_sessions(session_subparsers):
    count_parser = session_subparsers.add_parser("count")
    count_parser.add_argument(
        "--all", "-a", action="store_true", help="List all sessions in the database"
    )
    count_parser.add_argument("--today", "-t", action="store_true")
    count_parser.add_argument("--date", "-d", required=False)
    count_parser.add_argument("--scene", "-s", required=False)
    count_parser.add_argument("--project", "-p", required=False)
    count_parser.add_argument("--count", "-c", action="store_true", required=False)
    count_parser.add_argument("--wpm", "-w", action="store_true", required=False)
    count_parser.add_argument("--type", "-tp", nargs="*")
    count_parser.set_defaults(func=list_sessions)

    streak_parser = session_subparsers.add_parser("streak")
    streak_parser.set_defaults(func=get_off_days)
