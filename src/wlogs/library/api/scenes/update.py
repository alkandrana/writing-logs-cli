import sys

from wlogs import load_config
from wlogs.library.api.crud import send_auth_request
from wlogs.library.api.scenes.scene import get_scene_id
from wlogs.library.api.statuses.list import get_status_id
def build_patch(args):
    scene_id = get_scene_id(args.code)
    print(f"ID for scene with code {args.code}: {scene_id}")
    if args.property == "status":
        value = get_status_id(args.value)
        property = "statusId"
    else:
        value = args.value
        property = args.property
    payload = {
        "op": "replace",
        "path": property,
        "value": value
    }
    print(f"Payload: {payload}")
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/scenes/{scene_id}",
        "payload": [payload]
    }
    print(f"Request: {request}")
    return request

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

def update_scene(args):
    request = build_patch(args)
    send_update_request(request)

def parse_update_scene(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update")
    update_parser.add_argument("--code", "-c", type=str, required=True, help="Scene Code")
    update_parser.add_argument("--property", "-p", type=str, required=True, help="Which scene property to update")
    update_parser.add_argument("--value", "-v", type=str, required=True, help="The new value to set")
    update_parser.set_defaults(func=update_scene)