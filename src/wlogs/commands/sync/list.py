from pathlib import Path

from wlogs import load_config
from wlogs.utils.file_search import fast_search
from wlogs.utils.log_utils import (
    check_project_list,
    check_sync_projects,
    check_sync_scenes,
    get_projects_from_scenes,
    get_scenes_in_log,
)
from wlogs.utils.scene_utils import get_scene_details_from_csv, split_compound_id

from .sync_sessions import check_sync_sessions, get_records_from_csv


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
        master_scenelist = [f for f in scene_csv if "all" in f.name.lower()]
        if len(master_scenelist) == 1:
            scene_csv = master_scenelist[0]
        else:
            print(f"Multiple scenelists found for project {code}.")
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
        record_exists = any(str(s["id"]).lower() == sc.lower() for s in scene_records)
        # if no record is found, add that scene to list of manual scenes
        if not record_exists:
            manual_scenes.append(sc)
    return manual_scenes


def print_all_scenes(args):
    # returns a dictionary of project codes + scene lists
    scenes = get_scenes_in_log()
    print(f"Found {len(scenes)} scenes in log file.")
    projects = get_projects_from_scenes(scenes)
    if args.summarize:
        for proj in projects:
            print()
            scenes_in_proj = [sc for sc in scenes if sc.startswith(proj)]
            print(f"{len(scenes_in_proj)} scenes in project {proj.upper()}")
            choice = input(f"View all scenes in project {proj.upper()}? (y/n): ")
            if choice.lower() == "y":
                print(scenes_in_proj)

    # Get list of projects that do not exist in the database
    print("\nChecking for projects that need to be synced...")
    projects_to_create = check_sync_projects(projects)
    print("\nProjects that need to be synced: ", projects_to_create)

    # Get list of projects not in projects.csv
    print("\nChecking for projects that need to be manuallly created...")
    manual_projects = check_project_list(projects_to_create)
    print(f"Projects that need to be manually created: {manual_projects}")

    # Get list of csv scene paths and check filenames against list of project codes
    print("\nChecking for csv scene lists...")
    unlisted_projects = get_unlisted_projects(projects_to_create)
    print(f"Projects for which no scene list file exists: {unlisted_projects}")

    # Check list of scene codes for scenes that do not exist in the database
    print("\nChecking for scenes that need to be synced...")
    scenes_to_create = check_sync_scenes(scenes)

    # Find scene codes that don't exist in the database, check for corresponding records in csv file, and print the results
    print()
    project_groups = list({split_compound_id(sc)["project"] for sc in scenes_to_create})
    for proj in project_groups:
        scenes_in_proj = [
            sc for sc in scenes_to_create if sc.lower().startswith(proj.lower())
        ]
        print(f"\n{len(scenes_in_proj)} scenes need to be synced for project {proj}")
        choice = input("Show all? (y/n): ")
        if choice.lower() == "y":
            print(scenes_in_proj)
        if len(scenes_in_proj) > 0 and proj not in unlisted_projects:
            # find the csv file corresponding to the project code and load its scene records
            scene_records = get_scenelist_records(proj)
            manual_scenes = get_manual_scenes(proj, scenes_in_proj, scene_records)
            if len(manual_scenes) > 0:
                print(
                    f"{len(manual_scenes)} scenes that need to be manually created for project {proj}:"
                )
                choice = input("Show all? (y/n): ")
                if choice.lower() == "y":
                    print(manual_scenes)

            else:
                print(f"All {proj.upper()} scenes can be automatically created!")
    print()

    # Find sessions that are not in the database
    print("Checking for sessions that need to be synced...\n")
    local_sessions = get_records_from_csv(load_config()["log_file"])
    sessions_to_create = check_sync_sessions(local_sessions)
    print(f"\nFound {len(sessions_to_create)} sessions that need to be synced:\n")

    if len(sessions_to_create) > 0:
        choice = input("Show all? (y/n): ")
        if choice.lower() == "y":
            print([ses["id"] for ses in sessions_to_create])
    else:
        print("All sessions are already synced!")
    print()


def get_scene_csv() -> list[Path]:
    log_dir = Path(load_config()["log_file"]).parent
    scenelist_dir = next(iter(fast_search("scenes", log_dir))).parent
    scene_csvs = [f for f in scenelist_dir.iterdir() if "scenes" in f.name.lower()]
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
