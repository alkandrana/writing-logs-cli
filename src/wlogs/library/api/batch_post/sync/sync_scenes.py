import json
from typing import Any

from wlogs.commands.new_scene import convert_yaml_to_payload
from wlogs.library.api.batch_post.scenes import get_scene_details
from wlogs.library.api.batch_post.utils import post_record
from wlogs.library.dates import print_list_dict
from wlogs.library.file.scenes import load_yaml_header
from wlogs.library.file.search import find_file
from .string_utils import split_compound_id
from .log_utils import get_scenes_in_log, get_projects_from_log
from wlogs.library.api.crud import get_record_by_code
from wlogs.library.dates import print_list

def get_scene_from_repo(code: str):
    path = find_file(code.upper())
    if path and path.exists():
        details = load_yaml_header(path)
        return details
    return code.upper()
def check_sync_status(scene_codes: list[str]):
    scenes_to_add = []
    scene_records = []
    for sc in scene_codes:
        code = split_compound_id(sc)["scene"]
        res = get_record_by_code(code, "scenes")
        if res.status_code == 404:
            scenes_to_add.append(sc)
        else:
            scene_records.append(sc)
    return {"remote": scene_records, "local": scenes_to_add}
def sync_projects(book_codes: list[str]):
    books_to_add = []
    book_records = []
    for b in book_codes:
        res = get_record_by_code(b, "projects")
        if res.status_code == 404:
            books_to_add.append(b)
        else:
            book_records.append(res.json())
    return {"remote": book_records, "local": books_to_add}


def get_project_from_repo(code: str):
    path = find_file(code.upper())
    if path:
        specs = path / "novel.json"
        if specs.exists():
            with open(specs, "r", encoding="utf-8-sig") as f:
                novel = json.load(
                    f,
                )
            return novel
    return code.upper()


def get_local_project_details(project_codes: list[str]):
    local_projects = []
    for c in project_codes:
        print(f"\nGetting details for project {c}")
        project = get_project_from_repo(c)
        if not isinstance(project, str):
            local_projects.append(project)
    return local_projects


def get_unsaved_projects(
    local_codes: list[str], local_projects: list[dict[str, Any]]
) -> list[str]:
    local_keys = [p["id"] for p in local_projects]
    codes = [c.upper() for c in local_codes if c.upper() not in local_keys]
    return codes


def sync_scenes(args):
    if args.code:
        scenes = list_scenes_in_project(args.code)
        sync_scenes_in_project(scenes)
    else:
        book_codes = get_projects_from_log()
        for code in book_codes:
            sync_scenes_in_project(code)

def list_scenes_in_project(code: str):
    code = code.upper()
    print(f"Getting scenes for project {code}")
    scenes = get_scene_details(code)
    print_list_dict(scenes)
    return scenes
def sync_scenes_in_project(scenes):
    print("Posting scenes to API: ")
    for scene in scenes:
        post_record(scene, "scenes")
def sync_log_scenes(_):
    # 1. get scenes in log
    print("\nCollecting scenes referenced in log file...")
    scene_codes = get_scenes_in_log()
    #2. check all scenes against the api
    print("\nGetting list of scenes that need to be synced...")
    scenes_to_add = check_sync_status(scene_codes)["local"]
    if len(scenes_to_add) > 0:
    #3 check scenes against the filesystem
        scene_details = []
        print("\nSearching local filesystem for scene details...")
        for code in scenes_to_add:
            header = get_scene_from_repo(code)
            print(f"\n{header}")
            scene_details.append(header)
        #4 convert yaml headers to post details
        batch = []
        print("\nConverting scene headers to API-friendly payloads...")
        for scene in scene_details:
            batch.append(convert_yaml_to_payload(scene))
        for b in batch:
            print(f"\n{b}")
        #5 post unsynced scenes
        for payload in batch:
            post_record(payload, "scenes")
    else:
        print("All scenes already synced.")
    # project_codes = get_projects_from_log(scene_codes)
    # project_status = sync_projects(project_codes)
    # remote_projects = project_status["remote"]
    # local_projects = get_local_project_details(project_status["local"])
    # print("\nProjects already saved to the API:")
    # print_list_dict(remote_projects)
    # print("Projects existing locally:")
    # print_list_dict(local_projects)
    # unsaved = get_unsaved_projects(project_status["local"], local_projects)
    # if len(unsaved) > 0:
    #     print("Projects for which local details cannot be found:")
    #     print_list(unsaved)


def parse_batch_sync(sync_subparsers):
    project_parser = sync_subparsers.add_parser("scenes")
    project_parser.set_defaults(func=sync_log_scenes)
    # scenes_parser = sync_subparsers.add_parser("scenes")
    # scenes_parser.add_argument("--code", "-c", required=False)
    # scenes_parser.set_defaults(func=sync_scenes)

#1. get scenes in log
#2. check all scenes against api to get list that need to be added
#3 check unsynced scenes against filesystem to find out if there are scenes for which local details cannot be determined
#4 use filesystem yaml headers to get details for unsynced scenes
#5 post scenes to the api