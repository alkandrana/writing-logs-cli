import argparse
import sys

from wlogs import load_config
from wlogs.commands.auth import send_auth_request
from wlogs.utils.crud import build_patch, send_update_request
from wlogs.utils.scene_utils import get_scene_id
from wlogs.utils.status_utils import get_status_id


def update_scene(args: argparse.Namespace):
    scene_id = get_scene_id(args.code)
    print(f"ID for scene with code {args.code}: {scene_id}")
    payload = []
    if args.words != None:
        payload.append(build_patch("words", args.words))

    if args.name != None:
        payload.append(build_patch("name", args.name))
    if args.sequence != None:
        payload.append(build_patch("sequence", args.sequence))
    if args.status != None:
        value = get_status_id(args.status)
        payload.append(build_patch("statusId", value))
    if args.plotline != None:
        payload.append(build_patch("plotline", args.plotline))
    if args.chapter != None:
        payload.append(build_patch("chapter", args.chapter))
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/scenes/{scene_id}",
        "payload": payload,
    }
    c = input("Proceed? (y/n): ")
    if c.lower() == "y":
        send_update_request(request, "scene")


def parse_update_scene(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update")
    update_parser.add_argument(
        "--code", "-c", type=str, required=True, help="Scene Code"
    )
    update_parser.add_argument(
        "--name", "-n", type=str, required=False, help="Update scene name"
    )
    update_parser.add_argument(
        "--sequence", "-s", type=int, required=False, help="Update scene number"
    )
    update_parser.add_argument(
        "--words", "-w", type=int, required=False, help="Update scene word count."
    )
    update_parser.add_argument(
        "--status",
        "-st",
        type=str,
        required=False,
        help="Update scene status (pending, writing, finished, or aborted.",
    )
    update_parser.add_argument(
        "--plotline",
        "-p",
        type=str,
        required=False,
        help="Update scene's plotline (name of character whose story the scene contributes to)",
    )
    update_parser.add_argument(
        "--chapter",
        "-ch",
        type=str,
        required=False,
        help="Update scene's chapter name.",
    )
    update_parser.set_defaults(func=update_scene)
