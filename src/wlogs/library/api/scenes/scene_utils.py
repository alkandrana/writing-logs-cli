import csv
import sys
from pathlib import Path

from wlogs import load_config
from wlogs.commands import get_project_id
from wlogs.library.api.crud import check_record_exists

from ..statuses.list import get_status_id


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
