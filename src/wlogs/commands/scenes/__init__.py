from .list import parse_list_scenes
from .new_scene import parse_new_scene
from .update import parse_update_scene


def parse_scenes(subparsers):
    scenes_parser = subparsers.add_parser("scenes")
    scenes_subparsers = scenes_parser.add_subparsers(dest="subcommand")
    parse_new_scene(scenes_subparsers)
    parse_list_scenes(scenes_subparsers)
    parse_update_scene(scenes_subparsers)
