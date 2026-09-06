import sys
from typing import Any
from .sync.list import get_projects_from_log
from .sync.sync_scenes import (
    sync_projects,
    get_local_project_details,
    get_unsaved_projects,
)
from ..auth import send_auth_request
from .utils import transfer, post_record
from wlogs.library.api.auth import check_server_health
from wlogs import load_config


# def get_projects_from_log():
#     scene_codes = get_scenes_in_log()
#     booklist = []
#     for scene in scene_codes:
#         if "-" in scene:
#             proj = scene.split("-")[0]
#             if proj.lower() not in booklist:
#                 booklist.append(proj.lower())
#         else:
#             print(f"Project not found for scene: {scene}")
#     return booklist


def create_project_interactive(code):
    payload = {
        "code": code,
        "title": input("Book title: "),
        "goal": input("Target word count (optional): "),
    }
    if not payload["goal"]:
        payload["goal"] = 100000
    request = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/projects",
        "payload": payload,
    }
    res = send_auth_request(request)
    if res.status_code == 201:
        print(f"Project {code} created successfully")
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())


def format_projects_from_node(projects):
    booklist = []
    for b in projects:
        book = {
            "code": b["code"],
            "title": b["title"],
            "series": b["seriesTitle"],
            "goal": b["goal"],
        }
        booklist.append(book)
    return booklist


def format_projects_from_local(projects: list[dict[str, Any]]) -> list[dict]:
    batch = []
    for b in projects:
        book = {
            "code": b["id"],
            "title": b["title"],
        }
        if "series_title" in b:
            book["series"] = b["series_title"]
        if "goal" in b:
            book["goal"] = b["goal"]
        else:
            book["goal"] = 100000
        batch.append(book)
    return batch


def post_projects_from_file():
    print("Getting unsaved projects...")
    codes = get_projects_from_log()
    codes_to_add = sync_projects(codes)["local"]
    print("Converting project codes to project payload...")
    projects_to_add = get_local_project_details(codes_to_add)
    codes_to_add = get_unsaved_projects(codes_to_add, projects_to_add)
    if len(projects_to_add) > 0:
        batch = format_projects_from_local(projects_to_add)
        print("Saving projects to API")
        for p in batch:
            post_record(p, "projects")
    else:
        print("No local details for projects: ", codes_to_add)
        for c in codes_to_add:
            print(f"Building payload for project {c}:")
            create_project_interactive(c)


def batch_projects(args):
    if args.source == "api":
        url = load_config()["api_url"]
        if check_server_health(url):
            transfer(args.path, "projects", format_projects_from_node)
        else:
            print(
                "Server is down, or config is out of date. Update it with 'wlogs config api'."
            )
            sys.exit(1)
    elif args.source == "file":
        post_projects_from_file()
    else:
        print("Source must be one of 'api' or 'file'")
        sys.exit(1)


def parse_batch_projects(batch_subparsers):
    project_parser = batch_subparsers.add_parser("projects")
    project_parser.add_argument("--source", "-s", required=True)
    project_parser.set_defaults(func=batch_projects)
