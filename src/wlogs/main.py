import argparse

from .commands.auth import parse_auth
from .commands.plot import parse_plotter
from .commands.project import parse_project
from .commands.scenes import parse_scenes
from .commands.session import parse_session
from .commands.setup.config import parse_config
from .commands.sync import parse_sync


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    parse_config(subparsers)
    parse_auth(subparsers)
    parse_scenes(subparsers)
    parse_session(subparsers)
    parse_plotter(subparsers)
    parse_project(subparsers)
    parse_sync(subparsers)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
