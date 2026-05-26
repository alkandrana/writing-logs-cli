# Created by Rosa Lee Myers 02-12-2026 with help from ChatGPT
import argparse
from .commands.scene import parse_scene
from .commands.session import parse_session
from .commands.count import count_parser

def main():
    # print(HOME_DIR)
    parser = argparse.ArgumentParser(prog='wlogs')
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse_session(subparsers)
    count_parser(subparsers)
    parse_scene(subparsers)
    args = parser.parse_args()
    args.func(args)