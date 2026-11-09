from pathlib import Path

from wlogs import load_config
from wlogs.utils.log_utils import (
    check_sync_projects,
    check_sync_scenes,
    get_projects_from_scenes,
)
from wlogs.utils.scene_utils import get_scene_details_from_csv


def get_unlisted_projects(item_list: list[str]):
    scenelists = get_scene_csv()
    unregistered = []
    for it in item_list:
        result = check_scene_list(it, scenelists)
        if result:
            unregistered.append(result)
    return unregistered


def get_scenelist_records(code: str):
    scenelist_paths = get_scene_csv()
    scene_csv = [f for f in scenelist_paths if code.lower() in f.name.lower()]
    if len(scene_csv) > 1:
        print("Multiple scenelists found for project {code}.")
        for i, f in enumerate(scene_csv):
            print(f"{i}. {f}")
        choice = input("Please specify which scenelist you want to use: ")
        scene_csv = scene_csv[int(choice)]
    elif len(scene_csv) < 1:
        return []
    else:
        scene_csv = scene_csv[0]
    # load individual scene records from the csv file
    scenes = get_scene_details_from_csv(scene_csv)
    return scenes


def get_manual_scenes(
    project_code: str, codes: list[str], scene_records: list[dict[str, str | int]]
):
    manual_scenes = []
    for sc in codes:
        # check if corresponding scene record exists
        record_exists = any(
            str(s.get("code")).lower() == f"{project_code.lower()}-{sc.lower()}"
            for s in scene_records
        )
        # if no record is found, add that scene to list of manual scenes
        if not record_exists:
            manual_scenes.append(sc)
    return manual_scenes


def print_all_scenes(args):
    # returns a dictionary of project codes + scene lists
    projects = get_projects_from_scenes()
    if args.summarize:
        for proj in projects:
            print(f"Scenes for project: {proj.upper()}")
            print(projects[proj])

    # Get list of projects that do not exist in the database
    print("Checking for projects that need to be synced...")
    projects_to_create = check_sync_projects(projects)
    print("Projects that need to be synced: ", projects_to_create)

    # Get list of csv scene paths and check filenames against list of project codes
    print("Checking for csv scene lists...")
    unlisted_projects = get_unlisted_projects(projects_to_create)
    print(f"Projects that need to be manually created: {unlisted_projects}")

    # Check list of scene codes for scenes that do not exist in the database
    print("Checking for scenes that need to be synced...")
    scenes_to_create: dict[str, list[str]] = check_sync_scenes(projects)
    print("Scenes that need to be synced: ")

    # Find scene codes that don't exist in the database, check for corresponding records in csv file, and print the results
    for proj, scene_codes in scenes_to_create.items():
        if len(scene_codes) > 0 and proj not in unlisted_projects:
            # find the csv file corresponding to the project code and load its scene records
            scenes = get_scenelist_records(proj)
            manual_scenes = get_manual_scenes(proj, scene_codes, scenes)
            if len(manual_scenes) > 0:
                print(f"{proj}:")
                print(f"Scenes that need to be manually created: {manual_scenes}")
            else:
                print("All scenes can be automatically created!")


def get_scene_csv() -> list[Path]:
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
        "--summarize",
        "-sm",
        action="store_true",
        help="Report all scenes and projects found in log file",
    )
    list_parser.set_defaults(func=print_all_scenes)
