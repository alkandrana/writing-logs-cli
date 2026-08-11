import os, dotenv
import sys

from wlogs import load_config
from wlogs.commands import get_project_id
from wlogs.library.api.auth import send_auth_request
from wlogs.library.api.crud import get_record_id

dotenv.load_dotenv()


def get_one_scene(code: str):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/scenes/code/{code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        print(f"Error getting scene {res.status_code} {res.json()}")
        sys.exit(1)

def get_scene_by_name(name: str):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/scenes/name/{name}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        print(f"Error getting scene: {res.status_code} {res.json()} from {request['endpoint']}")
        sys.exit(1)

def print_scene(scenelist):
    if len(scenelist) > 1:
        print("Multiple scenes match that scene code. Make a selection: ")
        for i, sc in enumerate(scenelist):
            print(f"{i}: {sc['name']}, {sc['project']['code']}, {sc['plotline']}")
        choice = input("Select the appropriate number: ")
        scene = scenelist[int(choice)]
    else:
        scene = scenelist[0]
    print("Scene {scene['code']}: {scene['name']}\n")
    for key, value in scene.items():
        if not key == "project":
            print(f"{key}: {value}")
        elif key == "project" and value:
            print(f"project title: {value['title']}")

def get_scene_id(code: str):
    options = get_record_id(code, "scenes")
    print(options)
    if len(options) > 1:
        project_code = input("Multiple scenes match that scene code. Please specify the project code: ")
        project_id = get_project_id(project_code)
        scene_match = next((scene for scene in options if scene["projectId"] == project_id), None)
        scene_id = scene_match["id"]
    else:
        scene_id = options[0]["id"]
    return scene_id
def view_one_scene(args):
    if args.code:
        scenes = get_one_scene(args.code)
    elif args.name:
        scenes = get_scene_by_name(args.name)
    else:
        print("No search key submitted.")
        sys.exit(1)
    print_scene(scenes)


def parse_scene(scene_subparsers):
    one_parser = scene_subparsers.add_parser("one")
    one_parser.add_argument("--code", "-c", required=False)
    one_parser.add_argument("--project", "-p", required=False)
    one_parser.add_argument("--name", "-n", required=False)
    one_parser.set_defaults(func=view_one_scene)
