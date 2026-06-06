# Created by Rosa Lee Myers 02-12-2026 with help from ChatGPT
import argparse
from .commands.config import parse_config
from .commands.session import parse_session
from .commands.count import count_parser
from .commands.project import parse_project
from .commands.scene import parse_scene

def main():
    # print(HOME_DIR)
    parser = argparse.ArgumentParser(prog="wlogs")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse_config(subparsers)
    parse_session(subparsers)
    count_parser(subparsers)
    parse_scene(subparsers)
    parse_project(subparsers)
    args = parser.parse_args()
    args.func(args)

