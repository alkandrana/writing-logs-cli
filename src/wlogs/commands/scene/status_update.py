from .library import *
from ...utils.api import send_patch_request
def update_scene_status(args):
    status = args.status
    if status == "finished":
        summarize = input("Add a summary? (y/n): ")
        if summarize == "y":
            book_id = input("Enter project id: ")
            update_scene_data(book_id, args.scene)
    payload = {
        "status": status
    }
    updated = send_patch_request(payload, f"scenes/{args.scene}")
    print(f"Updated scene status for {args.scene}: {updated['status']}")
    print(updated)

def parse_update_scene_status(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update", help="Update scene details")
    update_parser.add_argument("--scene", required=True, help="Scene code")
    update_parser.add_argument("--status", required=True, help="Scene status")
    update_parser.set_defaults(func=update_scene_status)