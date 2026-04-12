import argparse
import sys
from ..utils.file_lib import *
from ..config import *
from ..utils.data_lib import *
from ..utils.api import *

def print_dict(data: dict[str, Any]):
    for key, value in data.items():
        print(f"{key}: {value}")

LOG_FILE = "master-writing-log"

# wlogs session start --scene AKT-LTN [--start_words 499]
def start_session(args):
    if session_in_progress():
        print(f"A session is already in progress: ")
        print_dict(load_session_data())
        print()
        args.subparser.print_help()
    else:
        data = {
            "scene_code": args.scene,
            "start_time": now_iso(),
            "date": datetime.now().date().strftime("%Y-%m-%d"),
            "start_words": args.start_words
        }
        path = state_path()
        write_json_to_file(path, data)
        print(f"Session started:")
        print_dict(load_session_data())

# wlogs session status
def session_status(_):
  if session_in_progress():
      print(f"Current session:")
      print_dict(load_session_data())
  else:
      print("No session currently running.")

# wlogs session cancel
def cancel_session(_):
    if not session_in_progress():
        print("No session running.")
    data = load_session_data()
    remove_session_data(state_path())
    print(f"Canceled session:")
    print_dict(data)

# wlogs session stop --words 566
def stop_session(args):
    data = validate_session(load_session_data())
    words = args.words - int(data["start_words"])
    remove_session_data(state_path())
    payload = convert_to_session(data, words)
    if not args.local:
        result = send_post_request(payload, "sessions")
        print(f"Successfully posted session:")
        print_dict(result)
    result = store_local_session(payload, LOG_FILE)
    print(f"Recorded: {result}")

def cmd_stop(args: argparse.Namespace) -> None:
    path = state_path()
    # Gather session data into variables
    data = validate_session(load_state(path))
    # Determine words:
    words: int | None = args.words
    stop_words: int | None = args.stop_words
    start_words: int | None = data.get("startWords", None)
    words = validate_words(start_words, stop_words, words)
    ### JSON DATA ###
    payload = {
        "sceneCode": data["sceneCode"],
        "date": data["date"],
        "startTime": data["startTime"],
        "stopTime": data["stopTime"],
        "words": int(words),
    }
    ### POST ###
    if not scene_exists(payload["sceneCode"]):
        print(f"Scene {payload['sceneCode']} does not exist.")
        add_scene = input("Would you like to create it? (y/n) ")
        if add_scene == "y":
            name = input("Scene Name: ")
            project = input("Project ID: ")
            scene_data = {
                "code": payload["sceneCode"],
                "sceneName": name,
                "bookCode": project,
                "statusName": "Writing"
            }
            post_results(scene_data, "scenes")
        else:
            sys.exit(0)

    created = post_results(payload, "sessions")
    # Only clear state if the POST succeeded
    remove_session_data(path)
    # Friendly output
    print(f"Submitted: {data["sceneCode"]} | {payload['words']} words | {data["startTime"]}")
    print(created)

def session_parser(subparsers):
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers(dest='command')
    start_parser = session_subparsers.add_parser("start", help="Start a writing session (stores local state, must be either caceled or saved before a new one can be started)")
    start_parser.add_argument("--scene", required=True, help="Scene code (e.g., AKT-JRM)")
    start_parser.add_argument("--start-words", type=int, default=0, help="Starting word count (optional)")
    start_parser.set_defaults(func=start_session, subparser=session_parser)

    status_parser = session_subparsers.add_parser("status", help="Show the currently running session")
    status_parser.set_defaults(func=session_status)

    cancel_parser = session_subparsers.add_parser("cancel", help="Discard the currently running session")
    cancel_parser.set_defaults(func=cancel_session)

    stop_parser = session_subparsers.add_parser("stop", help="Stop the current session and save it")
    stop_parser.add_argument("-d", "--diff", action="store_true", help="Calculate words as difference between --words and --start-words (--start-words argument must have been used when session was started).")
    stop_parser.add_argument("--local", action="store_true", help="Record session only in local log file (not posted to API)")
    stop_parser.add_argument("--words", required=True, type=int, default=None, help="Words written (direct)")
    stop_parser.set_defaults(func=stop_session)
    # session_parser.print_help()
