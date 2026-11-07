from wlogs.commands.count import get_all_sessions
from wlogs.library.api.crud import get_record_id
from wlogs import load_config
from wlogs.library.api.crud import send_fetch_request
from wlogs.library.api.scenes.scene import get_scene_id
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

def get_sessions_by_scene(scene_code):
        scene_id = get_scene_id(scene_code)
        print(f"Scene ID for {scene_code}: {scene_id}")
        request = {
            "method": "GET",
            "endpoint": f"{load_config()['api_url']}/sessions/scene/{scene_id}"
        }
        print(f"Requesting sessions for scene {scene_code} with request: {request}")
        sessions = send_fetch_request(request)
        if sessions:
            return sessions


def list_sessions(args):
    if args.scene:
        sessions = get_sessions_by_scene(args.scene)
    else:
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
    list_parser.add_argument("--scene", "-s", required=False, help="Scene Code")
    list_parser.set_defaults(func=list_sessions)

