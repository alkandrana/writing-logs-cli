from wlogs.commands.count import get_all_sessions
from datetime import datetime
import pandas as pd

pd.set_option(
    "display.max_rows",
    100,
    "display.max_columns",
    None,
    "display.expand_frame_repr",
    False,
)


def list_sessions(_):
    sessions = get_all_sessions()
    sessions = [
        {
            "date": ses["date"],
            "start": datetime.fromisoformat(ses["startTime"]).astimezone().isoformat()
            if ses["startTime"]
            else None,
            "stop": datetime.fromisoformat(ses["stopTime"]).astimezone().isoformat()
            if ses["stopTime"]
            else None,
            "words": ses["words"],
            "scene": ses["scene"]["code"],
        }
        for ses in sessions
    ]
    sessions.sort(key=lambda x: datetime.fromisoformat(x["date"]), reverse=True)
    dataframe = pd.DataFrame(sessions)
    print(dataframe)


def parse_list_sessions(session_subparsers):
    list_parser = session_subparsers.add_parser("list")
    list_parser.set_defaults(func=list_sessions)

