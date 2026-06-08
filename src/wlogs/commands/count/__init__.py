from .scene import parse_count_scene
from .session import parse_count_sessions


def count_parser(subparsers):
    count_parser = subparsers.add_parser("count")
    count_subparsers = count_parser.add_subparsers(dest="subcommand")
    parse_count_scene(count_subparsers)
    parse_count_sessions(count_subparsers)
