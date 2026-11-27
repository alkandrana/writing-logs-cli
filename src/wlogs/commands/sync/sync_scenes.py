import sys

from wlogs.utils.crud import (
    get_all_records,
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
    print("\nCollecting scenes referenced in log file...")
    scenes = get_scenes_in_log()
    print("\nGetting list of scenes that need to be synced...")
    scenes_to_add = check_sync_scenes(scenes)
    projects = list(
        {
            split_compound_id(sc)["project"]
            for sc in scenes_to_add
            if split_compound_id(sc)
        }
    )
    remote_projects = get_all_records("projects")
    print(f"Found {len(scenes_to_add)} scenes that need to be synced.")
    choice = input("Show all? (y/n): ")
    if choice.lower() == "y":
        print(scenes_to_add)
    for proj in projects:
        print(f"Getting scene details for project {proj}")
        filepath = get_csv_path(proj)
        scene_details = get_scene_details_from_csv(filepath) if filepath else []
        codes_to_add = [sc for sc in scenes_to_add if sc.startswith(proj)]
        if not any(p for p in remote_projects if p["code"] == proj):
            print(f"No project found for {proj}")
            sys.exit(1)
        project = next(p for p in remote_projects if p["code"] == proj)
        project_id = project["id"]
        for i, scene in enumerate(codes_to_add):
            print(f"Creating scene {i + 1} of {len(codes_to_add)}: {scene}")
            results = [
                sc for sc in scene_details if str(sc["id"]).lower() == scene.lower()
            ]
            print(f"Found match for scene {scene}: {results}")
            if len(results) > 1:
                print(
                    f"Scene code {scene} is not unique. Please check scene list for corrupted data."
                )
                sys.exit(1)
            elif len(results) < 1:
                print(f"Scene code {scene} not found in file.")
                scene_rec = {"code": scene, "projectId": project_id}
                get_scene_details(scene_rec)
                post_record(scene_rec, "scenes")
            else:
                scene_rec = results[0]
                scene_rec = convert_local_scene(scene_rec)
                print(f"Local scene {scene} converted to payload: {scene_rec}")
                choice = input("Proceed? (y/n): ")
                if choice.lower() == "y":
                    post_record(scene_rec, "scenes")
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
