from .start import parse_start_session
from .status import parse_session_status
from .cancel import parse_cancel_session
from .stop import parse_stop_session

def parse_session(subparsers):
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers(dest='subcommand')
    parse_start_session(session_subparsers)
    parse_stop_session(session_subparsers)
    parse_cancel_session(session_subparsers)
    parse_session_status(session_subparsers)