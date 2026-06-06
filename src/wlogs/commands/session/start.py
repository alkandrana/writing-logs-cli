from .Session import Session
from ...utils.data_lib import print_dict, get_current_timestamp
from ...utils.file_lib import write_json_to_file
from datetime import datetime

# wlogs session start --scene AKT-LTN [--start_words 499]
session = Session()


def handle_current_session(args):
    print("A session is already in progress: ")
    print_dict(session.data)
    print()
    args.subparser.print_help()


def build_start_session(args):
    return {
        "scene_code": args.scene,
        "start_time": get_current_timestamp(),
        "date": datetime.now().date().strftime("%Y-%m-%d"),
        "start_words": args.start_words,
    }


def save_start_session(data):
    write_json_to_file(session.state_path, data)


def print_start():
    print("Session started:")
    print_dict(session.load_session_data())


def start_session(args):
    ### Check for current session ###
    if session.data:
        handle_current_session(args)
    else:
        ### construct pre-session data ###
        data = build_start_session(args)
        ### print data to temp file ###
        save_start_session(data)
        ### Report to user ###
        print_start()


def parse_start_session(session_subparsers):
    start_parser = session_subparsers.add_parser(
        "start",
        help="Start a writing session (stores local state, must be either canceled or saved before a new one can be started)",
    )
    start_parser.add_argument(
        "--scene", required=True, help="Scene code (e.g., AKT-JRM)"
    )
    start_parser.add_argument(
        "--start-words", type=int, default=0, help="Starting word count (optional)"
    )
    start_parser.set_defaults(func=start_session)
