from .local_session_manager import SessionManager
from ...utils.data_lib import print_dict

ses_mng = SessionManager("master-writing-log")


def session_status(_):
    if ses_mng.session_in_progress():
        print("Current session:")
        print_dict(ses_mng.load_session_data())
    else:
        print("No session currently running.")


def parse_session_status(session_subparsers):
    status_parser = session_subparsers.add_parser(
        "status", help="Show the currently running session"
    )
    status_parser.set_defaults(func=session_status)
