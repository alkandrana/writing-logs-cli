import json
import sys
from typing import Any

from wlogs.commands.new_scene import convert_yaml_to_payload
from wlogs.library.api.batch_post.scenes import get_scene_details_from_file
from ...scenes.create_scene import get_scene_details, post_scene
from wlogs.library.api.batch_post.utils import post_record
from wlogs.library.dates import print_list_dict
from wlogs.library.file.scenes import load_yaml_header
from wlogs.library.file.search import find_file
from .string_utils import split_compound_id
from .log_utils import get_projects_from_scenes, check_sync_projects, check_sync_scenes
from wlogs.library.api.crud import get_record_by_code, check_record_exists
from ...projects.create import get_project_details, post_project
from wlogs.commands import get_project_id
from ...scenes.scene_utils import get_csv_path, get_scene_details_from_csv

# def get_scene_from_repo(code: str):
#     path = find_file(code.upper())
#     if path and path.exists():
#         details = load_yaml_header(path)
#         return details
#     return code.upper()
# def check_sync_status(scene_codes: list[str]):
#     scenes_to_add = []
#     scene_records = []
#     for sc in scene_codes:
#         code = split_compound_id(sc)["scene"]
#         res = get_record_by_code(code, "scenes")
#         if res.status_code == 404:
#             scenes_to_add.append(sc)
#         else:
#             scene_records.append(sc)
#     return {"remote": scene_records, "local": scenes_to_add}
# def sync_projects(book_codes: list[str]):
#     books_to_add = []
#     book_records = []
#     for b in book_codes:
#         res = get_record_by_code(b, "projects")
#         if res.status_code == 404:
#             books_to_add.append(b)
#         else:
#             book_records.append(res.json())
#     return {"remote": book_records, "local": books_to_add}
#
#
# def get_project_from_repo(code: str):
#     path = find_file(code.upper())
#     if path:
#         specs = path / "novel.json"
#         if specs.exists():
#             with open(specs, "r", encoding="utf-8-sig") as f:
#                 novel = json.load(
#                     f,
#                 )
#             return novel
#     return code.upper()
#
#
# def get_local_project_details(project_codes: list[str]):
#     local_projects = []
#     for c in project_codes:
#         print(f"\nGetting details for project {c}")
#         project = get_project_from_repo(c)
#         if not isinstance(project, str):
#             local_projects.append(project)
#     return local_projects
#
#
# def get_unsaved_projects(
#     local_codes: list[str], local_projects: list[dict[str, Any]]
# ) -> list[str]:
#     local_keys = [p["id"] for p in local_projects]
#     codes = [c.upper() for c in local_codes if c.upper() not in local_keys]
#     return codes
#
#
# def sync_scenes(args):
#     if args.code:
#         scenes = list_scenes_in_project(args.code)
#         sync_scenes_in_project(scenes)
#     else:
#         book_codes = get_projects_from_scenes()
#         for code in book_codes:
#             sync_scenes_in_project(code)
#
# def list_scenes_in_project(code: str):
#     code = code.upper()
#     print(f"Getting scenes for project {code}")
#     scenes = get_scene_details_from_file(code)
#     print_list_dict(scenes)
#     return scenes
# def sync_scenes_in_project(scenes):
#     print("Posting scenes to API: ")
#     for scene in scenes:
#         post_record(scene, "scenes")
def sync_log_projects():
    # 1. get scenes in log
    print("\nCollecting projects referenced in log file...")
    project_complex = get_projects_from_scenes()
    #2. check all scenes against the api
    print("\nGetting list of projects that need to be synced...")
    projects_to_add = check_sync_projects(project_complex)

    #3. add projects to api
    if len(projects_to_add) > 0:
        print(f"Adding projects: {projects_to_add}")
        for p in projects_to_add:
            project = get_project_details(p)
            post_project(project)
        print(f"Synced projects: {projects_to_add}")
    else:
        print("ALl projects are already synced.")

def sync_log_scenes():
    print("\nCollecting scenes referenced in log file...")
    project_complex = get_projects_from_scenes() # returns a dict where keys are project codes and values are lists of scene codes
    print("\nGetting list of scenes that need to be synced...")
    scenes_to_add = check_sync_scenes(project_complex)
    print(scenes_to_add)
    for proj in scenes_to_add:
        print(f"Getting scene details for project {proj}")
        filepath = get_csv_path(proj)
        scene_details = get_scene_details_from_csv(filepath) if filepath else []
        codes_to_add: list[str] = scenes_to_add[proj]
        if not check_record_exists(proj, "projects"):
            project = get_project_details(proj)
            post_project(project)
        project_id = get_project_id(proj)
        for i, sc in enumerate(codes_to_add):
            print(f"Creating scene {i + 1} of {len(codes_to_add)}")
            code = f"{proj}-{sc}"
            results = [sc for sc in scene_details if sc['code'].lower() == code.lower()]
            if len(results) > 1:
                print(f"Scene code {code} is not unique.")
                sys.exit(1)
            elif len(results) < 1:
                print(f"Scene code {code} not found in file.")
                project_id = get_project_id(proj)
                scene = { "code": code, "projectId": project_id }
                get_scene_details(scene)
                post_scene(scene)
            else: 
                scene = results[0]
                post_scene(scene)
    print(f"Synced scenes: {scenes_to_add}")

def sync_log(args):
    if args.projects:
        sync_log_projects()
    elif args.scenes:
        sync_log_scenes()
    else:
        sync_log_projects()
        sync_log_scenes()


def parse_batch_sync(sync_subparsers):
    project_parser = sync_subparsers.add_parser("log")
    project_parser.add_argument("--scenes", "-sc", action="store_true", help="Sync scenes only (you will be prompted to create projects that don't already exist)")
    project_parser.add_argument("--projects", "-p", action="store_true", help="Sync projects only.")
    project_parser.set_defaults(func=sync_log)
