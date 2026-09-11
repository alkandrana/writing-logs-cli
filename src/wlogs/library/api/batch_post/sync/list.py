from .log_utils import check_sync_projects, check_sync_scenes
from .log_utils import get_projects_from_scenes, get_scenes_in_log

def print_all_scenes(args):
    projects = get_projects_from_scenes() # returns a dictionary of project codes + scene lists
    for proj in projects:
        print(f"Scenes for project: {proj.upper()}")
        print(projects[proj])
    if args.sync:
        print("Checking for projects that need to be synced...")
        projects_to_create = check_sync_projects(projects)
        print("Projects that need to be synced: ", projects_to_create)
        print("Checking for scenes that need to be synced...")
        scenes_to_create: dict[str, list[str]] = check_sync_scenes(projects)
        print("Scenes that need to be synced: ")
        for proj in scenes_to_create:
            if len(scenes_to_create[proj]) > 0:
                print(proj.upper())
                print(scenes_to_create[proj])




def parse_sync_list(sync_subparsers):
    list_parser = sync_subparsers.add_parser("list")
    list_parser.add_argument("--sync", "-s", action="store_true", help="Check which scenes need to be added to the API")
    list_parser.set_defaults(func=print_all_scenes)
