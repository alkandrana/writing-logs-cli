from wlogs.config import API_URL, HOME_DIR
from .scene_manager import SceneManager
from ...utils.api import Api

API = Api(API_URL)
scene_mng = SceneManager(HOME_DIR)


def update_scene_status(args):
    status = args.status
    if status == "finished":
        summarize = input("Add a summary? (y/n): ")
        if summarize == "y":
            book_id = input("Enter project id: ")
            header = scene_mng.get_yaml_header(args.scene)
            scene_mng.add_yaml_summary(header)
            scene_mng.write_json_header(header, book_id)
    payload = {"status": status}
    updated = API.send_patch_request(payload, f"scenes/{args.scene}")
    print(f"Updated scene status for {args.scene}: {updated['status']}")
    print(updated)


def update_scene_count(args):
    header = scene_mng.get_yaml_header(args.scene)
    word_count = header["word_count"]
    payload = {"words": word_count}
    updated = API.send_patch_request(payload, f"scenes/{args.scene}")
    print(f"Updated scene count for {args.scene}: {payload['words']}")
    print(updated)


def parse_update_scene(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update", help="Update scene details")
    status_parser = update_parser.add_parser("status", help="Update scene status")
    status_parser.add_argument("--scene", required=True, help="Scene code")
    status_parser.add_argument("--status", required=True, help="Scene status")
    status_parser.set_defaults(func=update_scene_status)

    count_parser = update_parser.add_parser("count", help="Update scene's word count")
    count_parser.add_argument("--scene", required=True, help="Scene code")
    count_parser.add_argument("--words", required=True, help="New word count")
    status_parser.set_defaults(func=update_scene_count)
