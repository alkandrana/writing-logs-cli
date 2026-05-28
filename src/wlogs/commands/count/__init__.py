from .scene import parse_count_scene


def count_parser(subparsers):
    count_parser = subparsers.add_parser("count")
    count_subparsers = count_parser.add_subparsers(dest="command")
    parse_count_scene(count_subparsers)
