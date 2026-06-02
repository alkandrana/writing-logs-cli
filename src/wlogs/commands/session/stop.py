import sys

from ...utils.data_lib import print_dict
from wlogs.commands.session.local_session_manager import SessionManager
from ...utils.api import Api
from ...config import API_URL

API = Api(API_URL)
SESSION_MANAGER = SessionManager("master-writing-log")


# wlogs session stop --words 566
def stop_session(args):
    print("Loading session data from file...")
    data = SESSION_MANAGER.load_session_data()
    SESSION_MANAGER.handle_no_data(data)
    words = args.words - int(data["start_words"])
    print("Retrieving scene from server...")
    scene_id = SESSION_MANAGER.get_scene_id(data["scene_code"], API)
    print("Formatting session data...")
    payload = SESSION_MANAGER.convert_to_session(data, words)
    if not args.local:
        print("Sending session to server...")
        payload["sceneId"] = scene_id
        result = API.send_post_request(payload, "sessions")
        print("Successfully posted session:")
        print_dict(result)
    print("Saving session to local log file...")
    result = SESSION_MANAGER.store_local_session(payload)
    print("Clearing state...")
    SESSION_MANAGER.remove_session_data()
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
