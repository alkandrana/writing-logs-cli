import csv
import sys
from pathlib import Path

from wlogs import load_config

from .crud import get_all_records
from .scene_utils import split_compound_id


def get_scenes_in_log():
    log_file = load_config()["log_file"]
    if Path(log_file).exists():
        with open(log_file, "r") as f:
            reader = csv.DictReader(f)
            # returns a list of unique scene codes
            scenes = list({row["scene"].upper() for row in reader})
        return scenes
    else:
        print("Log file could not be found.")
        sys.exit(1)


# 2. using the resultant list of scenes, get all projects referenced
def get_projects_from_scenes(scene_codes) -> list[str]:
    booklist = list(
        {
            split_compound_id(sc)["project"]
            for sc in scene_codes
            if split_compound_id(sc)
        }
    )
    return booklist


def check_sync_projects(projects: list[str]) -> list[str]:
    projects_to_create = []
    remote_projects = get_all_records("projects")
    for proj in projects:
        if not any(p for p in remote_projects if p["code"].lower() == proj.lower()):
            projects_to_create.append(proj)
    return projects_to_create


def get_project_records():
    project_csv = Path(load_config()["log_file"]).parent / "projects.csv"
    if project_csv.exists():
        with open(project_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            project_records = [row for row in reader]
        return project_records
    else:
        print(
            "No projects.csv found in log directory. All projects must be manually created."
        )
        return []


def check_project_list(projects: list[str]):
    manual_projects = []
    project_records = get_project_records()
    for p in projects:
        if not any(pr for pr in project_records if pr["code"].lower() == p.lower()):
            manual_projects.append(p)
    return manual_projects


def check_sync_scenes(scene_list: list[str]) -> list[str]:
    scenes_to_create = []
    remote_scenes = get_all_records("scenes")
    for scene in scene_list:
        if not any(sc for sc in remote_scenes if sc["code"].lower() == scene.lower()):
            scenes_to_create.append(scene)
    return scenes_to_create
