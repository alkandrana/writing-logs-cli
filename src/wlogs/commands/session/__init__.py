from .count import parse_count_sessions
from .session import parse_create_session


def parse_session(subparsers):
    session_parser = subparsers.add_parser("session")
    session_subparsers = session_parser.add_subparsers(dest="subcommand")
    parse_create_session(session_subparsers)
    parse_count_sessions(session_subparsers)
