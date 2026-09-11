import sys
import csv
from pathlib import Path
from wlogs import load_config
from ..statuses.list import get_status_id
from wlogs.commands import get_project_id

def get_csv_path(code: str) -> Path | None:
    log_loc = Path(load_config()["log_file"])
    log_dir = log_loc.parent
    search = [f for f in log_dir.rglob(f"*{code}*")]
    if len(search) == 1:
        filepath = search[0]
    else:
        print("Something went wrong.")
        sys.exit(1)
    return filepath
    
def get_scene_details_from_csv(filepath: Path) -> list[dict[str, str | int]]:
    with open(filepath, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    scenes = []
    for row in data:
        status: str = convert_status(row['Status'])
        status_id = get_status_id(status)
        project = row['ID'][0:row['ID'].index("-")] if "-" in row['ID'] else None
        if project:
            project_id = get_project_id(project)
        else:
            project_id = 0
        scene = {
                    'code': row['ID'], 
                    'sequence': row['Sequence'], 
                    'name': row['Name'], 
                    'words': row['Words'], 
                    'plotline': row['Plotline'], 
                    'statusId': status_id, 
                    'chapter': row.get('Chapter', None),
                    'projectId': project_id 
                }
        scenes.append(scene)
    return scenes

def convert_status(status: str) -> str:
     translation = ""
     if status == "First Draft" or status == "Revised Draft" or status == "Final Draft" or status == "Done":
         translation = "finished"
     elif status == "In Progress":
         translation = "writing"
     elif status == "Aborted":
         translation = "aborted"
     else:
         translation = "pending"
     return translation

