from ...crud import check_record_exists
from .string_utils import split_compound_id
from .log_utils import get_projects_from_log, get_scenes_in_log
def print_all_scenes(args):
    scene_codes = get_scenes_in_log()
    projects = get_projects_from_log(scene_codes) # returns a dictionary of project codes + scene lists
    for proj in projects.keys():
        print(f"Scenes for project: {proj.upper()}")
        print(projects[proj])
    if args.sync:
        print(f"Checking for projects that need to be synced...")
        projects_to_create = check_sync_projects(projects)
        print("Projects that need to be synced: ", projects_to_create)
        print("Checking for scenes that need to be synced...")
        scenes_to_create = check_sync_scenes(projects)
        print("Scenes that need to be synced: ", scenes_to_create)

def check_sync_projects(projects: dict[str, list[str]]) -> list[str]:
    projects_to_create = []
    for proj in projects.keys():
        if not check_record_exists(proj, "projects"):
            projects_to_create.append(proj)
    return projects_to_create

def check_sync_scenes(projects: dict[str, list[str]]):
    scenes_to_create = {}
    for key, value in projects.items():
        if key not in scenes_to_create:
            scenes_to_create[key] = []
        for code in value:
            if code not in scenes_to_create[key]:
                if not check_record_exists(f"{key}-{code}", "scenes"):
                    scenes_to_create[key].append(code)
    return scenes_to_create



def parse_sync_list(sync_subparsers):
    list_parser = sync_subparsers.add_parser("list")
    list_parser.add_argument("--sync", "-s", action="store_true", help="Check which scenes need to be added to the API")
    list_parser.set_defaults(func=print_all_scenes)