from local_session_manager import SessionManager
from ...utils.data_lib import print_dict

ses_mng = SessionManager("master-writing-log")


# wlogs session cancel
def cancel_session(_):
    if not ses_mng.session_in_progress():
        print("No session running.")
    data = ses_mng.load_session_data()
    ses_mng.remove_session_data()
    print("Canceled session:")
    print_dict(data)


def parse_cancel_session(session_subparsers):
    cancel_parser = session_subparsers.add_parser(
        "cancel", help="Discard the currently running session"
    )
    cancel_parser.set_defaults(func=cancel_session)

