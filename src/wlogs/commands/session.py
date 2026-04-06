from ..utils.file_lib import *
from ..config import *
from ..utils.data_lib import *
from ..utils.api import *

# wlogs session start --scene AKT-LTN [--start_words 499]
# start_session():
#    if session_in_progress():
#       print(f"A session is already in progress: {session_in_progress()}")
#       output_usage()
#   else:
#       data = get_start_data()
#       write_to_file(data)
#       print(f"Session started: {data}")

def cmd_start(args: argparse.Namespace) -> None:
    path = state_path()
    current = load_state(path)
    if current:
        print("A session is already in progress:", file=sys.stderr)
        print(f"    sceneCode:  {current.get('sceneCode')}", file=sys.stderr)
        print(f"    startTime:  {current.get('startTime')} (elapsed {format_elapsed(current.get('startTime',''))})", file=sys.stderr)
        print("Use `wlogs cancel` to discard it, or `wlogs stop` to submit it.", file=sys.stderr)
        sys.exit(2)
    data: dict[str, Any] = {
        "sceneCode": args.scene,
        "startTime": now_iso(),
        "date": datetime.now().date().strftime("%Y-%m-%d"),
    }
    if args.start_words is not None:
        data["startWords"] = args.start_words

    save_state(path, data)
    msg = f"Started: {data['sceneCode']} @ {data['startTime']}"
    if "startWords" in data:
        msg += f" (startWords {data['startWords']})"
    print(msg)

# wlogs session status
# session_status():
#   if session_in_progress():
#       print(f"Current session: {session_in_progress()}")
#   else:
#       print("No session currently running.")
def cmd_status(_: argparse.Namespace) -> None:
    path = state_path()
    data = load_state(path)
    if not data:
        print("No session in progress.")
        return

    start_time = data.get("startTime", "?")
    scene = data.get("sceneCode", "?")
    start_words = data.get("startWords", None)

    print(f"Session in progress:")
    print(f"    sceneCode:  {scene}")
    print(f"    startTime:  {start_time} (elapsed {format_elapsed(start_time)})")
    if start_words is not None:
        print(f"    startWords: {start_words}")

# wlogs session cancel
# cancel_session():
    # data = get_file_data()
    # remove_file_data()
    # print(f"Canceled session: {data}")
def cmd_cancel(_: argparse.Namespace) -> None:
    path = state_path()
    if not path.exists():
        print("No session to cancel.")
        return
    data = load_state(path)
    clear_state(path)
    print(f"Canceled session: {data.get('sceneCode', '?')} @ {data.get('startTime', '?')}")

# wlogs session stop
# stop_session():
#   data = get_file_data()
#   words = get_words()
#   payload = convert_to_session()
#   post_session()

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
    clear_state(path)
    # Friendly output
    print(f"Submitted: {data["sceneCode"]} | {payload['words']} words | {data["startTime"]}")
    print(created)

def session_parser(subparsers):
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers(dest='command')
    start_parser = session_subparsers.add_parser("start", help="Start a writing session (stores local state)")
    start_parser.add_argument("--scene", required=True, help="Scene code (e.g., AKT-JRM)")
    start_parser.add_argument("--start-words", type=int, default=None, help="Starting word count (optional)")
    start_parser.set_defaults(func=cmd_start)

    status_parser = session_subparsers.add_parser("status", help="Show the currently running session")
    status_parser.set_defaults(func=cmd_status)

    cancel_parser = session_subparsers.add_parser("cancel", help="Discard the currently running session")
    cancel_parser.set_defaults(func=cmd_cancel)

    stop_parser = session_subparsers.add_parser("stop", help="Stop the current session and POST it to the API")
    stop_parser.add_argument("--stop-words", type=int, default=None, help="Stopping words count (delta computed if startWords exists)")
    stop_parser.add_argument("--words", type=int, default=None, help="Words written (direct)")
    stop_parser.set_defaults(func=cmd_stop)