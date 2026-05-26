from .library import *
# wlogs session start --scene AKT-LTN [--start_words 499]

def handle_current_session(args):
    print(f"A session is already in progress: ")
    print_dict(load_session_data())
    print()
    args.subparser.print_help()

def build_start_session(args):
    return {
        "scene_code": args.scene,
        "start_time": now_iso(),
        "date": datetime.now().date().strftime("%Y-%m-%d"),
        "start_words": args.start_words
    }

def save_start_session(data):
    path = state_path()
    write_json_to_file(path, data)

def print_start():
    print(f"Session started:")
    print_dict(load_session_data())
def start_session(args):
    ### Check for current session ###
    if session_in_progress():
        handle_current_session(args)
    else:
        ### construct pre-session data ###
        data = build_start_session(args)
        ### print data to temp file ###
        save_start_session(data)
        ### Report to user ###
        print_start()


def parse_start_session(session_subparsers):
    start_parser = session_subparsers.add_parser("start", help="Start a writing session (stores local state, must be either caceled or saved before a new one can be started)")
    start_parser.add_argument("--scene", required=True, help="Scene code (e.g., AKT-JRM)")
    start_parser.add_argument("--start-words", type=int, default=0, help="Starting word count (optional)")
    start_parser.set_defaults(func=start_session)
