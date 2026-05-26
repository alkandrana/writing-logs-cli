from .library import *
from ...utils.api import send_post_request
from ...config import LOG_FILE
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

def parse_stop_session(session_subparsers):
    stop_parser = session_subparsers.add_parser("stop", help="Stop the current session and save it")
    stop_parser.add_argument("-d", "--diff", action="store_true",
                             help="Calculate words as difference between --words and --start-words (--start-words argument must have been used when session was started).")
    stop_parser.add_argument("--local", action="store_true",
                             help="Record session only in local log file (not posted to API)")
    stop_parser.add_argument("--words", required=True, type=int, default=None, help="Words written (direct)")
    stop_parser.set_defaults(func=stop_session)