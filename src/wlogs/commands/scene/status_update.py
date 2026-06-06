import sys
from .Scene import Scene
from ...utils.api import Api
print("Loading status update module")
API = Api()
print("Api initialized")

def update_scene_status(args):
    print("Printing status arguments: ", args)
    scene = Scene(args.scene)
    status = args.status
    if status == "finished":
        summarize = input("Add a summary? (y/n): ")
        if summarize == "y":
            header = scene.get_yaml_header()
            scene.add_yaml_summary()
            scene.write_json_header()
    payload = {"status": status}
    scene_id = scene.get_scene_id()
    print(f"Id for scene {args.scene}: {scene_id}")
    updated = API.patch_results(payload, f"scenes/{scene_id}")
    print(f"Updated scene status for {args.scene}: {updated['status']}")
    print(updated)


def update_scene_count(args):
    print("Printing scene count arguments: ", args)
    scene = Scene(args.scene)
    header = scene.get_yaml_header()
    word_count = header["word_count"]
    payload = {"words": word_count}
    scene_id = scene.get_scene_id()
    updated = API.patch_results(payload, f"scenes/{scene_id}")
    print(f"Updated scene count for {args.scene}: {payload['words']}")
    print(updated)


def parse_update_scene(scene_subparsers):
    update_parser = scene_subparsers.add_parser("update", help="Update scene details")
    update_subparsers = update_parser.add_subparsers(dest="command")
    status_parser = update_subparsers.add_parser("status", help="Update scene status")
    status_parser.add_argument("--scene", required=True, help="Scene code")
    status_parser.add_argument("--status", required=True, help="Scene status")
    status_parser.set_defaults(func=update_scene_status)

    count_parser = update_subparsers.add_parser("count", help="Update scene's word count")
    count_parser.add_argument("--scene", required=True, help="Scene code")
    count_parser.set_defaults(func=update_scene_count)
