from ...utils.data_lib import print_dict
from wlogs.commands.session.local_session_manager import SessionManager
from ...utils.api import Api
from ...config import API_URL

API = Api(API_URL)
SESSION_MANAGER = SessionManager("master-writing-log")


# wlogs session stop --words 566
def stop_session(args):
    data = SESSION_MANAGER.load_session_data()
    SESSION_MANAGER.handle_no_data(data)
    words = args.words - int(data["start_words"])
    payload = SESSION_MANAGER.convert_to_session(data, words)
    if not args.local:
        result = API.send_post_request(payload, "sessions")
        print("Successfully posted session:")
        print_dict(result)
    result = SESSION_MANAGER.store_local_session(payload)
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
    stop_parser.add_argument(
        "--words", required=True, type=int, default=None, help="Words written (direct)"
    )
    stop_parser.set_defaults(func=stop_session)
