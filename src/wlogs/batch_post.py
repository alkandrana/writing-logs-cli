from src.wlogs.utils.api import *
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import csv

TZ = ZoneInfo("America/Los_Angeles")
def parse_time(s_time: str):
    if s_time:
        s_time = s_time.strip()
        fmt = "%H:%M:%S" if s_time.count(":") == 2 else "%H:%M"
        return datetime.strptime(s_time, fmt).time() if s_time else None
    else:
        return None
def build_timestamp(s_date, time_str):
    date_col = datetime.strptime(s_date, "%Y-%m-%d").date()
    start_time = parse_time(time_str)
    start_time = datetime.combine(date_col, start_time, tzinfo=TZ)
    return start_time

def post_session_from_file(session: dict[str, Any]):
    url = f"{BASE_URL}/sessions"
    if not scene_exists(session["sceneCode"]):
        scene = {
            "code": session["sceneCode"],
            "sceneName": ""
        }
        try:
            res = requests.post(f"{BASE_URL}/scenes", json=scene, timeout=10)
            print(f"Successfully created new scene {session['sceneCode']}")
            res.raise_for_status()
        except HTTPError as e:
            print(e)
            print(e.response.json())
            print(e.response.text)
    try:
        res = requests.post(url, json=session, timeout=10)
        res.raise_for_status()
        print(f"Successfully created session {session['oldId']}")
    except HTTPError as e:
        print(e)
        print(e.response.json())

def get_sessions(filename: str):
    # get data from file
    data = []
    with open(filename, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            start = build_timestamp(row["date"], row["start"]) if row["start"] else None
            stop = build_timestamp(row["date"], row["stop"]) if row["stop"] else None
            if stop and start and stop < start:
                stop += timedelta(days=1)
            start = start.isoformat() if start else None
            stop = stop.isoformat() if stop else None
            words = int(row["words"])
            notes = row["note"] if row["note"] else ""
            record = {
                "oldId": row["session_id"],
                "date": row["date"],
                "startTime": start,
                "stopTime": stop,
                "sceneCode": row["scene_id"],
                "words": words,
                "notes": notes
            }
            data.append(record)
    return data

def prep():
    data = get_sessions("/Users/rosamyers/repos/writing/writing-logs/master-writing-log.csv")
    test_sample = data[0:10]
    return test_sample