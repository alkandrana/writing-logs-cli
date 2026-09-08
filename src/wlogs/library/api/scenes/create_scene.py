import os
import sys

from wlogs import load_config
from wlogs.commands import get_project_id
from wlogs.library.api.auth import send_auth_request
from wlogs.library.api.crud import get_status_values
from wlogs.library.api.projects.list import get_projects
from wlogs.library.api.statuses.list import get_status_id


def build_body(args, project_id):
    statuses = get_status_values()
    print(statuses)
    body = {"code": args.code, "name": args.name, "projectId": project_id}
    if args.sequence:
        body["sequence"] = args.sequence
    if args.words:
        body["words"] = args.words
    if args.status:
        status_id = [st["id"] for st in statuses if st["name"].lower() == args.status.lower()][0]
        body["statusId"] = status_id
    if args.mc:
        body["plotline"] = args.mc
    return body


def post_scene(body):
    scene_req = {
        "method": "POST",
        "endpoint": f"{load_config()["api_url"]}/scenes",
        "payload": body,
    }
    print(body)
    response = send_auth_request(scene_req)
    if 200 <= response.status_code < 300:
        print(f"Scene successfully saved to the API: {response.status_code}")
    elif response.status_code == 409:
        print("Scene already exists. Skipping...")
    else:
        print("There was an error: ", response.status_code, response.reason, response.json())

def get_scene_details(scene):
    name = input("Enter scene name/description: ")
    sequence = input("Enter scene number (where in the story the scene falls; optional: ")
    words = input("Enter word count for scene: ")
    status = input("Enter scene status (pending, writing, finished, aborted; default pending): ")
    plotline = input("Enter name of POV character for this scene (optional): ")
    chapter = input("Enter chapter title (optional): ")
    scene["name"] = name
    scene["plotline"] = plotline
    scene["chapter"] = chapter
    try:
        scene["sequence"] = int(sequence)
        scene["words"] = int(words)
    except ValueError:
        print("Scene number and words must be valid integers")
        sys.exit(1)
    scene["status"] = get_status_id(status)

def get_scene_codes(code):
    if "-" in code:
        project = code[0:code.index("-")]
        scene_code = code
    else:
        project_list = get_projects()
        print("Scene project could not be determined.")
        for i, project in enumerate(project_list):
            print(f"{i}. {project['code']}: {project['title']}")
        choice = input("Select the corresponding number: ")
        project = project_list[int(choice)]["code"]
        scene_code = f"{project}-{code}"
    return {"project": project, "scene": scene_code}

def create_scene(args):
    code = args.code
    codes = get_scene_codes(code)
    project_id = get_project_id(codes["project"])
    scene = {
        "code": codes["scene"],
        "projectId": project_id
    }
    get_scene_details(scene)
    print(scene)
    # post_scene(scene)


def parse_create_scene(scene_subparsers):
    create_parser = scene_subparsers.add_parser("create")
    create_parser.add_argument("--code", "-c", required=True)
    create_parser.set_defaults(func=create_scene)