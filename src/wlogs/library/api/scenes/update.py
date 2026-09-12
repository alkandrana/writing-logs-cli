import sys
import argparse
from wlogs.library.api.scenes.scene import get_scene_id
from wlogs.library.api.statuses.list import get_status_id
from wlogs import load_config
from wlogs.library.api.auth import send_auth_request

def build_patch(property_name: str, value: str | int) -> dict[str, str | int]:
    return { 
            "op": "replace", 
            "path": f"/{property_name}", 
            "value": value 
    }
    
def send_update_request(request):
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print("Scene updated successfully")
    elif res.status_code == 404:
        print("Scene not found.")
        sys.exit(1)
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())
        sys.exit(1)

def update_scene(args: argparse.Namespace):
    scene_id = get_scene_id(args.code)
    print(f"ID for scene with code {args.code}: {scene_id}")
    payload = []
    if args.words:
        payload.append(build_patch("words", args.words))

    if args.name:
        payload.append(build_patch("name", args.name))
    if args.sequence:
        payload.append(build_patch("sequence", args.sequence))
    if args.status:
        value = get_status_id(args.status)
        payload.append(build_patch("statusId", value))
    if args.plotline:
        payload.append(build_patch("plotline", args.plotline))
    if args.chapter:
        payload.append(build_patch("chapter", args.chapter))
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/scenes/{scene_id}",
        "payload": payload
    }
    send_update_request(request)

def parse_update_scene(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update")
    update_parser.add_argument("--code", "-c", type=str, required=True, help="Scene Code")
    update_parser.add_argument("--name", "-n", type=str, required=False, help="Update scene name")
    update_parser.add_argument("--sequence", "-s", type=int, required=False, help="Update scene number")
    update_parser.add_argument("--words", "-w", type=int, required=False, help="Update scene word count.")
    update_parser.add_argument("--status", "-st", type=str, required=False, help="Update scene status (pending, writing, finished, or aborted.")
    update_parser.add_argument("--plotline", "-p", type=str, required=False, help="Update scene's plotline (name of character whose story the scene contributes to)")
    update_parser.add_argument("--chapter", "-ch", type=str, required=False, help="Update scene's chapter name.")
    update_parser.set_defaults(func=update_scene)
