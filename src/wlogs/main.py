# Created by Rosa Lee Myers 02-12-2026 with help from ChatGPT
from .config import build_parser
from .commands.session import *

def main():
    parser = build_parser()
    session_parser(parser)
    args = parser.parse_args()
    args.func(args)