# Created by Rosa Lee Myers 02-12-2026 with help from ChatGPT
import argparse

def main():
    parser = argparse.ArgumentParser(prog='wlogs')
    subparsers = parser.add_subparsers(dest='command')

    session_parser = subparsers.add_parser("session")
    session_sub = session_parser.add_subparsers(dest="action")

    add_parser = session_sub.add_parser("add")
    add_parser.add_argument("--scene", required=True)
    add_parser.add_argument("--start", required=True)
    add_parser.add_argument("--stop", required=True)
    add_parser.add_argument("--words", type=int, required=True)

    args = parser.parse_args()
    print(args)