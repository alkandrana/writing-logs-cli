import argparse
import sys

from wlogs.utils.crud import build_patch, get_record_id, send_update_request


def update_scene(args: argparse.Namespace):
    scene_id = get_record_id(args.code, "scenes")
    print(f"ID for scene with code {args.code}: {scene_id}")
    payload = []
    if args.words != None:
        payload.append(build_patch("words", args.words))

    if args.name != None:
        payload.append(build_patch("name", args.name))
    if args.sequence != None:
        payload.append(build_patch("sequence", args.sequence))
    if args.status != None:
        value = get_record_id(args.status, "status", "name")
        if not value:
            print(f"Status record could not be found for status {args.status}.")
            sys.exit(1)
        payload.append(build_patch("statusId", value))
    if args.plotline != None:
        payload.append(build_patch("plotline", args.plotline))
    if args.chapter != None:
        payload.append(build_patch("chapter", args.chapter))
    if scene_id:
        c = input("Proceed? (y/n): ")
        if c.lower() == "y":
            send_update_request(payload, "scenes", scene_id)
    else:
        print(f"Error: no record matching {args.code} found.")
        sys.exit(1)


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
