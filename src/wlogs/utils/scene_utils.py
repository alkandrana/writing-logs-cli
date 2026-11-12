import csv
import sys
from pathlib import Path
from typing import Any

from wlogs import load_config
from wlogs.commands.auth import send_auth_request

from .crud import check_record_exists
from .project_utils import get_project_by_code, get_project_id
from .status_utils import get_status_id


def split_compound_id(compound_id: str) -> dict[str, str]:
    codes = {}
    if "-" in compound_id:
        parts = compound_id.split("-")
        codes["project"] = parts[0]
        codes["scene"] = parts[1]
    return codes


def post_scene(body: dict[str, str | int]):
    scene_req: dict[str, object] = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/scenes",
        "payload": body,
    }
    print(body)
    response = send_auth_request(scene_req)
    if 200 <= response.status_code < 300:
        print(f"Scene successfully saved to the API: {response.status_code}")
    elif response.status_code == 409:
        print("Scene already exists. Skipping...")
    else:
        print(
            "There was an error: ",
            response.status_code,
            response.reason,
            response.json(),
        )


def get_scene_details(scene):
    print(f"\nAdd details for scene {scene['code']}: ")
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
    scene["name"] = name
    scene["plotline"] = plotline
    scene["chapter"] = chapter
    try:
        scene["sequence"] = int(sequence) if sequence else 0
        scene["words"] = int(words) if words else 0
    except ValueError:
        print("Scene number and words must be valid integers")
        sys.exit(1)
    scene["statusId"] = get_status_id(status)


def get_scenes_by_project(code) -> list[dict[str, Any]]:
    proj = get_project_by_code(code)
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
        print(f"\n{res.status_code}: {res.json()}")
        sys.exit(1)


def get_scenes_by_code(code: str) -> list[dict[str, Any]]:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/scenes/code/{code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    elif res.status_code == 404:
        print(
            f"Scene {code} doesn't exist yet. Create it with 'wlogs scenes create {code}'."
        )
        sys.exit(0)
    else:
        print(f"Error getting scene {res.status_code} {res.json()}")
        sys.exit(1)


def get_one_scene(scene_code: str, project_code: str) -> dict[str, str | int] | None:
    scenes = get_scenes_by_code(scene_code)
    if len(scenes) > 1:
        scene = [sc for sc in scenes if sc["project"]["code"] == project_code]
        if len(scene) > 1:
            print(
                f"Error: multiple scenes match those identifiers: {scene}\n\
                  Consider updating or deleting the duplicate scenes."
            )
            sys.exit(1)
        elif len(scene) < 1:
            print(
                f"No scenes found in {project_code} matching scene {scene[0]['code']}."
            )
            sys.exit(0)
        else:
            scene = scene[0]
            return scene


def get_scene_id(code: str) -> int:
    scene = get_scenes_by_code(code)
    if len(scene) != 1:
        print(f"Multiple scenes with code {code} exist.")
        project_code = input("Specify code of project for the desired scene: ")
        scene = get_one_scene(code, project_code)
    else:
        scene = scene[0]
    scene_id = int(scene["id"]) if scene else 0
    return scene_id


def get_scene_by_id(scene_id: int) -> dict[str, str | int]:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/scenes/{scene_id}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    elif res.status_code == 404:
        print("No scene found matching that id.")
        sys.exit(0)
    else:
        print(
            f"An error occurred: {res.status_code} {res.json()} from {request['endpoint']}"
        )
        sys.exit(1)


def build_patch(property_name: str, value: str | int) -> dict[str, str | int]:
    return {"op": "replace", "path": f"/{property_name}", "value": value}


def send_update_request(payload: list[dict[str, str | int]], scene_id: int):
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/scenes/{scene_id}",
        "payload": payload,
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print(f"Scene {payload[0]['path']} updated successfully")
    elif res.status_code == 404:
        print("Scene not found.")
        sys.exit(1)
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())
        sys.exit(1)


def get_csv_path(code: str) -> Path | None:
    log_loc = Path(load_config()["log_file"])
    log_dir = log_loc.parent
    search = [f for f in log_dir.rglob(f"*{code.upper()}*")]
    if len(search) == 1:
        filepath = search[0]
    elif len(search) == 0:
        print(
            f"No file found for project {code}. You will need to manually enter details for any scenes in this project."
        )
        filepath = None
    else:
        print(f"Something went wrong: {search}")
        sys.exit(1)
    return filepath


def get_scene_details_from_csv(filepath: Path) -> list[dict[str, str | int]]:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        data = [{k.lower(): v for k, v in row.items()} for row in reader]
    scenes = []
    for row in data:
        status: str = convert_status(row["status"])
        status_id = get_status_id(status)
        project = row["id"][0 : row["id"].index("-")] if "-" in row["id"] else None
        if project and check_record_exists(project, "projects"):
            project_id = get_project_id(project)
        else:
            project_id = 0
        scene = {
            "code": row["id"],
            "sequence": row["sequence"] if row["sequence"] else 0,
            "name": row["name"],
            "words": row["words"] if row["words"] else 0,
            "plotline": row["plotline"],
            "statusId": status_id,
            "chapter": row.get("chapter", None),
            "projectId": project_id,
        }
        scenes.append(scene)
    return scenes


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
