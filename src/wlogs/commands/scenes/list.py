import sys
from typing import Any

import pandas as pd

from wlogs import load_config
from wlogs.library.api.auth import send_auth_request
from wlogs.library.api.scenes.scenes_by_project import get_scenes_by_project


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
        scene = [sc for sc in scenes if sc["project"]["code"] == project_code]
        if len(scene) > 1:
            print(
                f"Error: multiple scenes match those identifiers: {scene}\n\
                  Consider updating or deleting the duplicate scenes."
            )
            sys.exit(1)
        elif len(scene) < 1:
            print(
                f"No scenes found in {project_code} matching scene {scene[0]['code']}."
            )
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
        print(
            f"Error getting scene: {res.status_code} {res.json()} from {request['endpoint']}"
        )
        sys.exit(1)


def print_scene(scenelist):
    scenelist = [
        {
            "code": sc["code"],
            "sequence": sc["sequence"],
            "name": sc["name"],
            "chapter": sc["chapter"] if sc["chapter"] else "",
            "words": sc["words"],
            "status": sc["status"]["name"] if sc["status"] else "",
            "plotline": sc["plotline"] if sc["plotline"] else "",
            "project": sc["project"]["title"] if sc["project"] else "",
        }
        for sc in scenelist
    ]
    df = pd.DataFrame(scenelist)
    print(df)


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
        criterion = f"code {args.code}"
        scenes = get_scenes_by_code(args.code)
    elif args.name:
        criterion = f"name {args.name}"
        scenes = get_scene_by_name(args.name)
    elif args.project:
        criterion = f"project {args.project}"
        scenes = get_scenes_by_project(args.project)
    else:
        print("No search key submitted.")
        sys.exit(1)
    print(f"\n{len(scenes)} scenes match {criterion}:\n")
    print_scene(scenes)


def parse_list_scenes(scene_subparsers):
    list_parser = scene_subparsers.add_parser("list")
    list_parser.add_argument("--code", "-c", required=False)
    list_parser.add_argument("--project", "-p", required=False)
    list_parser.add_argument("--name", "-n", required=False)
    list_parser.set_defaults(func=view_one_scene)
