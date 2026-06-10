import sys

from ..scene.Scene import Scene
from ...utils.data_lib import print_dict, get_current_timestamp
from wlogs.commands.session.Session import Session
from ...utils.api import Api
print("Initializing api in stop session")
API = Api()
SESSION = Session()
if SESSION.data:
    scene = Scene(f"{SESSION.data["project_code"]}-{SESSION.data["scene_code"]}")





# wlogs session stop --words 566
def stop_session(args):
    SESSION.handle_no_data()
    SESSION.data["words"] = args.words - int(SESSION.data["start_words"])
    if not SESSION.data["stop_time"]:
        SESSION.data["stop_time"] = get_current_timestamp()
    if not args.local:
        if API.record_exists("scenes/code", SESSION.data["scene_code"]):
            SESSION.data["scene_id"] = scene.get_scene_id()
        else:
            print(f"Scene {SESSION.data["scene_code"]} doesn't exist yet. Create it with 'wlogs scene new' before proceeding.")
            sys.exit(1)
        payload = SESSION.convert_to_session()
        print("Sending session to server...")
        result = API.send_post_request(payload, "sessions")
        print("Successfully posted session:")
        print_dict(result)
    print("Saving session to local log file...")
    result = SESSION.store_local_session()
    SESSION.remove_session_data()
    print(f"Recorded: {result}")


def parse_stop_session(session_subparsers):
    stop_parser = session_subparsers.add_parser(
        "stop", help="Stop the current session and save it"
    )
    stop_parser.add_argument(
        "-d",
        "--diff",
        action="store_true",
        help="Calculate words as difference between --words and --start-words (--start-words argument must have been used when session was started).",
    )
    stop_parser.add_argument(
        "--local",
        action="store_true",
        help="Record session only in local log file (not posted to API)",
    )
    stop_parser.add_argument("-m", "--mode", choices=["d", "e", "r", "p"], default="d")
    stop_parser.add_argument(
        "--words", required=True, type=int, default=None, help="Words written (direct)"
    )
    stop_parser.set_defaults(func=stop_session)
