# Created by Rosa Lee Myers, 2026-03-14
from .new import parse_new_scene
from .status_update import parse_update_scene_status
def parse_scene(subparsers):
    scene_parser = subparsers.add_parser("scene")
    scene_subparsers = scene_parser.add_subparsers(dest="command")
    parse_new_scene(scene_subparsers)
    parse_update_scene_status(scene_subparsers)