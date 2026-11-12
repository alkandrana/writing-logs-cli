from .list import parse_sync_list
from .sync_scenes import parse_batch_sync
from .sync_sessions import parse_batch_sessions


def parse_sync(subparsers):
    sync_parser = subparsers.add_parser("sync")
    sync_subparsers = sync_parser.add_subparsers(dest="subcommand")
    parse_sync_list(sync_subparsers)
    parse_batch_sync(sync_subparsers)
    parse_batch_sessions(sync_subparsers)
