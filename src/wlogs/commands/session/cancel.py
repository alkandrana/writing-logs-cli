from .library import *
# wlogs session cancel
def cancel_session(_):
    if not session_in_progress():
        print("No session running.")
    data = load_session_data()
    remove_session_data(state_path())
    print(f"Canceled session:")
    print_dict(data)

def parse_cancel_session(session_subparsers):
    cancel_parser = session_subparsers.add_parser("cancel", help="Discard the currently running session")
    cancel_parser.set_defaults(func=cancel_session)