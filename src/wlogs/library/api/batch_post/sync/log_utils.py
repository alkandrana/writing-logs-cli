from pathlib import Path
import csv, sys
from wlogs import load_config
from ...crud import check_record_exists
from .string_utils import split_compound_id
def get_scenes_in_log():
    log_file = load_config()["log_file"]
    if Path(log_file).exists():
        with open(log_file, "r") as f:
            reader = csv.DictReader(f)
            # returns a list of unique scene codes
            scenes = list(set([row["scene_id"].upper() for row in reader]))
        return scenes
    else:
        print("Log file could not be found.")
        sys.exit(1)


# 2. using the resultant list of scenes, get all projects referenced
def get_projects_from_scenes() -> dict[str, list[str]]:
    scene_codes = get_scenes_in_log()
    booklist = {}
    for scene in scene_codes:
        code_parts = split_compound_id(scene) # returns a dictionary
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
