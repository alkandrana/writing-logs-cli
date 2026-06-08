from .Session import Session
from ...utils.data_lib import print_dict

session = Session()

# wlogs session cancel
def cancel_session(_):
    if not session.session_in_progress():
        print("No session running.")
    data = session.load_session_data()
    session.remove_session_data()
    print("Canceled session:")
    print_dict(data)


def parse_cancel_session(session_subparsers):
    cancel_parser = session_subparsers.add_parser(
        "cancel", help="Discard the currently running session"
    )
    cancel_parser.set_defaults(func=cancel_session)
