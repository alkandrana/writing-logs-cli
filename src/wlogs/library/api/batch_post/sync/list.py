from pathlib import Path

from wlogs import load_config

from ...scenes.scene_utils import get_scene_details_from_csv
from .log_utils import check_sync_projects, check_sync_scenes, get_projects_from_scenes


def print_all_scenes(args):
    projects = (
        get_projects_from_scenes()
    )  # returns a dictionary of project codes + scene lists
    for proj in projects:
        print(f"Scenes for project: {proj.upper()}")
        print(projects[proj])
    if args.sync:
        print("Checking for projects that need to be synced...")
        projects_to_create = check_sync_projects(projects)
        print("Projects that need to be synced: ", projects_to_create)
        print("Checking for csv scene lists...")
        scenelists = get_scene_csv()
        unregistered = []
        for p in projects_to_create:
            result = check_scene_list(p, scenelists)
            if result:
                unregistered.append(result)
        print(f"Projects that need to be manually created: {unregistered}")
        print("Checking for scenes that need to be synced...")
        scenes_to_create: dict[str, list[str]] = check_sync_scenes(projects)
        print("Scenes that need to be synced: ")
        for proj, scene_codes in scenes_to_create.items():
            if len(scene_codes) > 0:
                unregistered_scenes = []
                print(proj.upper())
                print(scene_codes)
                if proj not in unregistered:
                    scene_csv = next(
                        f for f in scenelists if proj.lower() in f.name.lower()
                    )
                    scenes = get_scene_details_from_csv(scene_csv)
                    for sc in scene_codes:
                        match = [
                            s
                            for s in scenes
                            if s["code"].lower() == f"{proj.lower()}-{sc.lower()}"
                        ]
                        if len(match) == 0:
                            unregistered_scenes.append(sc)
                print(f"Scenes that need to be manually created: {unregistered_scenes}")


def get_scene_csv():
    log_dir = Path(load_config()["log_file"]).parent
    scene_csvs = [f for f in log_dir.iterdir() if "scenes" in f.name.lower()]
    return scene_csvs


def check_scene_list(code: str, filelist: list[Path]):
    for f in filelist:
        if code.lower() in f.name.lower():
            return
    return code


def parse_sync_list(sync_subparsers):
    list_parser = sync_subparsers.add_parser("list")
    list_parser.add_argument(
        "--sync",
        "-s",
        action="store_true",
        help="Check which scenes need to be added to the API",
    )
    list_parser.set_defaults(func=print_all_scenes)
