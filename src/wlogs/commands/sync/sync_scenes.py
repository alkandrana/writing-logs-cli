import sys

from wlogs.utils.crud import (
    post_record,
)
from wlogs.utils.log_utils import (
    check_sync_projects,
    check_sync_scenes,
    get_project_records,
    get_projects_from_scenes,
    get_scenes_in_log,
)
from wlogs.utils.project_utils import (
    get_project_details,
)
from wlogs.utils.scene_utils import (
    convert_local_scene,
    get_csv_path,
    get_scene_details,
    get_scene_details_from_csv,
    split_compound_id,
)


def sync_log_projects():
    # 1. get scenes in log
    print("\nCollecting projects referenced in log file...")
    scenes = get_scenes_in_log()
    projects = get_projects_from_scenes(scenes)
    # 2. check all projects against the api
    print("\nGetting list of projects that need to be synced...")
    projects_to_add = check_sync_projects(projects)

    # 3. add projects to api
    if len(projects_to_add) > 0:
        print(f"Adding projects: {projects_to_add}")
        project_records = get_project_records()
        for p in projects_to_add:
            project = next(
                (pr for pr in project_records if pr["code"].lower() == p.lower()), {}
            )
            if not project:
                print(f"No project details found for project {p.upper()}")
                project = get_project_details(p)
            post_record(project, "projects")
        print(f"Synced projects: {projects_to_add}")
    else:
        print("ALl projects are already synced.")


def sync_log_scenes():
    scenes = get_scenes_in_log()
    scenes_to_add = check_sync_scenes(scenes)
    projects = list(
        {
            split_compound_id(sc)["project"]
            for sc in scenes_to_add
            if split_compound_id(sc)
        }
    )
    scenelist_paths = [get_csv_path(p) for p in projects]
    local_scene_records = [get_scene_details_from_csv(f) for f in scenelist_paths if f]
    local_scene_records = [sc for proj in local_scene_records for sc in proj]
    print(f"Found {len(scenes_to_add)} scenes that need to be synced.")
    choice = input("Show all? (y/n): ")
    if choice.lower() == "y":
        print(scenes_to_add)
    for i, scene_code in enumerate(scenes_to_add):
        print(f"Creating scene {i + 1} of {len(scenes_to_add)}: {scene_code}")
        results = [
            sc
            for sc in local_scene_records
            if str(sc["id"]).lower() == scene_code.lower()
        ]
        if len(results) > 1:
            print(
                f"Scene code {scene_code} is not unique. Please check scene list for corrupted data."
            )
            sys.exit(1)
        elif len(results) < 1:
            print(f"Scene code {scene_code} not found in file.")
            scene_record = get_scene_details(scene_code)
            post_record(scene_record, "scenes")
        else:
            scene_record = results[0]
            scene_record = convert_local_scene(scene_record)
            print(f"Local scene {scene_code} converted to payload: {scene_record}")
            choice = input("Proceed? (y/n): ")
            if choice.lower() == "y":
                post_record(scene_record, "scenes")
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
    project_parser.add_argument(
        "--scenes",
        "-sc",
        action="store_true",
        help="Sync scenes only (you will be prompted to create projects that don't already exist)",
    )
    project_parser.add_argument(
        "--projects", "-p", action="store_true", help="Sync projects only."
    )
    project_parser.set_defaults(func=sync_log)
