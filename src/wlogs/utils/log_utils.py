import csv
import sys
from pathlib import Path

from wlogs import load_config

from .crud import check_record_exists, get_all_records
from .scene_utils import split_compound_id, get_scenes_by_project


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
def get_projects_from_scenes() -> dict[str, list[str]]:
    scene_codes = get_scenes_in_log()
    booklist = {}
    for scene in scene_codes:
        code_parts = split_compound_id(scene)  # returns a dictionary
        if not "project" in code_parts:
            print(f"Project not found for scene: {scene}")
        else:
            proj = code_parts["project"].lower()
            if proj not in booklist:
                booklist[proj] = []
            booklist[proj].append(code_parts["scene"].lower())
    return booklist


def check_sync_projects(projects: dict[str, list[str]]) -> list[str]:
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


def check_sync_scenes(projects: dict[str, list[str]]):
    scenes_to_create: dict[str, list[str]] = {}
    remote_scenes = get_all_records("scenes")
    for key, value in projects.items():
        print(f"Checking scenes for project {key}")
        for code in value:
            if not any(
                sc
                for sc in remote_scenes
                if sc["code"].lower() == f"{key}-{code}".lower()
            ):
                if key not in scenes_to_create:
                    scenes_to_create[key] = []
                if code not in scenes_to_create[key]:
                    scenes_to_create[key].append(code)
    return scenes_to_create
