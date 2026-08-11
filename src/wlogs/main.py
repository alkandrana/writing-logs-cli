import argparse

from .library.api.batch_post.sync import parse_sync
from .library.api.projects import parse_projects
from .library.api.scenes import parse_scenes
from .commands.session import parse_session
from .commands.setup.config import parse_config
from .commands.batch import parse_batch_scenes
from .commands.plot import parse_plotter
from .commands.new_scene import parse_new_scene
from .commands.count import parse_count
from .library.file import parse_file
from .library.api.auth import parse_auth
from .commands.project import parse_project


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    parse_config(subparsers)
    parse_auth(subparsers)
    parse_scenes(subparsers)
    parse_new_scene(subparsers)
    parse_session(subparsers)
    parse_count(subparsers)
    parse_sync(subparsers)
    parse_batch_scenes(subparsers)
    parse_file(subparsers)
    parse_plotter(subparsers)
    parse_project(subparsers)
    parse_projects(subparsers)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
