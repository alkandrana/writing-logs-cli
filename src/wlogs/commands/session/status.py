from .Session import Session
from ...utils.data_lib import print_dict

session = Session()


def session_status(_):
    if session.data:
        print("Current session:")
        print_dict(session.data)
    else:
        print("No session currently running.")


def parse_session_status(session_subparsers):
    status_parser = session_subparsers.add_parser(
        "status", help="Show the currently running session"
    )
    status_parser.set_defaults(func=session_status)
