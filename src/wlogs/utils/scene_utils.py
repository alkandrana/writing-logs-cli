import csv
import sys
from pathlib import Path
from typing import Any

from wlogs import load_config
from wlogs.commands.auth import print_error_message, send_auth_request

from .crud import (
    check_record_exists,
    get_all_records,
    get_record_by_code,
    get_record_id,
)


def split_compound_id(compound_id: str) -> dict[str, str]:
    codes = {}
    if "-" in compound_id:
        parts = compound_id.split("-")
        codes["project"] = parts[0]
        codes["scene"] = parts[1]
    return codes


def get_scene_details(code: str) -> dict[str, str | int]:
    print(f"\nAdd details for scene {code}: ")
    name = input("Enter scene name/description: ")
    sequence = input(
        "Enter scene number (where in the story the scene falls; optional): "
    )
    words = input("Enter word count for scene: ")
    status = input(
        "Enter scene status (pending, writing, finished, aborted; default pending): "
    )
    plotline = input("Enter name of POV character for this scene (optional): ")
    chapter = input("Enter chapter title (optional): ")
    project_code = (
        split_compound_id(code)["project"] if split_compound_id(code) else None
    )
    if not project_code:
        project_code = input("Enter project code: ")
    project_id = get_record_id(project_code, "projects")
    new_scene: dict[str, str | int] = {
        "name": name,
        "plotline": plotline,
        "chapter": chapter,
    }
    try:
        new_scene["sequence"] = int(sequence) if sequence else 0
        new_scene["words"] = int(words) if words else 0
        new_scene["projectId"] = project_id
    except ValueError:
        print("Scene number and words must be valid integers")
        sys.exit(1)
    new_scene["statusId"] = get_record_id(status, "status", "name")
    return new_scene


def get_scenes_by_project(code) -> list[dict[str, Any]]:
    proj = get_record_by_code(code, "projects")
    project_id = proj["id"]
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/scenes/project/{project_id}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        scenes = res.json()
        scenes.sort(key=lambda sc: sc["sequence"])
        return scenes
    else:
        print_error_message(res)
        sys.exit(1)


def get_csv_path(code: str) -> Path | None:
    log_loc = Path(load_config()["log_file"])
    log_dir = log_loc.parent
    search = [f for f in log_dir.rglob(f"*{code.upper()}*")]
    if len(search) == 0:
        print(
            f"No file found for project {code}. You will need to manually enter details for any scenes in this project."
        )
        filepath = None
    elif len(search) == 1:
        filepath = search[0]
    elif len([f for f in search if "all" in f.name.lower()]) == 1:
        filepath = next(f for f in search if "all" in f.name.lower())
    else:
        print(f"Something went wrong: {search}")
        sys.exit(1)
    return filepath


def get_scene_details_from_csv(filepath: Path) -> list[dict[str, str | int]]:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        data = [{k.lower(): v for k, v in row.items()} for row in reader]
        return data


def convert_local_scene(local_scene):
    status: str = convert_status(local_scene["status"])
    status_options = get_all_records("status")
    status_id = next(
        (st["id"] for st in status_options if st["name"].lower() == status), None
    )
    project = (
        local_scene["id"][0 : local_scene["id"].index("-")]
        if "-" in local_scene["id"]
        else None
    )
    if project and check_record_exists(project, "projects"):
        project_id = get_record_id(project, "projects")
    else:
        project_id = 0
    scene = {
        "code": local_scene["id"],
        "sequence": local_scene["sequence"] if local_scene["sequence"] else 0,
        "name": local_scene["name"],
        "words": local_scene["words"] if local_scene["words"] else 0,
        "plotline": local_scene["plotline"],
        "statusId": status_id,
        "chapter": local_scene.get("chapter", None),
        "projectId": project_id,
    }
    return scene


def convert_status(status: str) -> str:
    translation = ""
    if (
        status == "First Draft"
        or status == "Revised Draft"
        or status == "Final Draft"
        or status == "Done"
    ):
        translation = "finished"
    elif status == "In Progress":
        translation = "writing"
    elif status == "Aborted":
        translation = "aborted"
    else:
        translation = "pending"
    return translation
