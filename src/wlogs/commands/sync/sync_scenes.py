import sys

from wlogs.utils.crud import check_record_exists, get_record_id, post_record
from wlogs.utils.log_utils import (
    check_sync_projects,
    check_sync_scenes,
    get_project_records,
    get_projects_from_scenes,
)
from wlogs.utils.project_utils import (
    get_project_details,
)
from wlogs.utils.scene_utils import (
    convert_local_scene,
    get_csv_path,
    get_scene_details,
    get_scene_details_from_csv,
)


def sync_log_projects():
    # 1. get scenes in log
    print("\nCollecting projects referenced in log file...")
    project_complex = get_projects_from_scenes()
    # 2. check all scenes against the api
    print("\nGetting list of projects that need to be synced...")
    projects_to_add = check_sync_projects(project_complex)

    # 3. add projects to api
    if len(projects_to_add) > 0:
        print(f"Adding projects: {projects_to_add}")
        projects = get_project_records()
        for p in projects_to_add:
            project = next(
                (pr for pr in projects if pr["code"].lower() == p.lower()), {}
            )
            if not project:
                print(f"No project details found for project {p.upper()}")
                project = get_project_details(p)
            post_record(project, "projects")
        print(f"Synced projects: {projects_to_add}")
    else:
        print("ALl projects are already synced.")


def sync_log_scenes():
    print("\nCollecting scenes referenced in log file...")
    project_complex = (
        get_projects_from_scenes()
    )  # returns a dict where keys are project codes and values are lists of scene codes
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
            post_record(project, "projects")
        project_id = get_record_id(proj, "projects")
        for i, sc in enumerate(codes_to_add):
            print(f"Creating scene {i + 1} of {len(codes_to_add)}")
            code = f"{proj}-{sc}"
            results = [
                sc for sc in scene_details if str(sc["id"]).lower() == code.lower()
            ]
            print(f"Found match for scene {code}: {results}")
            if len(results) > 1:
                print(
                    f"Scene code {code} is not unique. Please check scene list for corrupted data."
                )
                sys.exit(1)
            elif len(results) < 1:
                print(f"Scene code {code} not found in file.")
                project_id = get_record_id(proj, "projects")
                scene = {"code": code, "projectId": project_id}
                get_scene_details(scene)
                post_record(scene, "scenes")
            else:
                scene = results[0]
                scene = convert_local_scene(scene)
                print(f"Local scene {code} converted to payload: {scene}")
                choice = input("Proceed? (y/n): ")
                if choice.lower() == "y":
                    post_record(scene, "scenes")
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
