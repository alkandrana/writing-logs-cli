import sys
from typing import Any
from wlogs import load_config
from wlogs.commands import get_project_id
from wlogs.library.api.auth import send_auth_request
from wlogs.library.api.crud import get_record_id

def get_scenes_by_code(code: str) -> list[dict[str, Any]]:
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

def get_one_scene(scene_code: str, project_code: str) -> dict[str, str | int] | None:
    scenes = get_scenes_by_code(scene_code)
    if len(scenes) > 1:
        scene = [sc for sc in scenes if sc['project']['code'] == project_code]
        if len(scene) > 1:
            print(f"Error: multiple scenes match those identifiers: {scene}\n\
                  Consider updating or deleting the duplicate scenes.")
            sys.exit(1)
        elif len(scene) < 1:
            print(f"No scenes found in {project_code} matching scene {scene[0]['code']}.")
            sys.exit(0)
        else:
            scene = scene[0]
            return scene

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
    print(f"Scene {scene['code']}: {scene['name']}\n")
    for key, value in scene.items():
        if not key == "project":
            print(f"{key}: {value}")
        elif key == "project" and value:
            print(f"project title: {value['title']}")

def get_scene_id(code: str) -> int:
    scene = get_scenes_by_code(code)
    if len(scene) != 1:
        print(f"Multiple scenes with code {code} exist.")
        project_code = input("Specify code of project for the desired scene: ")
        scene = get_one_scene(code, project_code)
    else:
        scene = scene[0]
    scene_id = int(scene["id"]) if scene else 0
    return scene_id

def view_one_scene(args):
    if args.code:
        scenes = get_scenes_by_code(args.code)
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
