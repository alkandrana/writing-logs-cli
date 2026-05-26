import sys
from pathlib import Path
from typing import Any
import json
import yaml
from wlogs.utils.data_lib import get_novel_parent

# NOVEL_ROOT = get_novel_parent()
def get_last_line(path):
    with open(path, 'r') as f:
        last_line = None
        for line in f:
            if line.strip():
                last_line = line
    return last_line

def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))



def save_state(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")



def get_novel_directory():
    projects_home = Path(get_novel_parent())
    if not projects_home.exists():
        print("Could not resolve root directory. Make sure directory is in home folder and try again.")
        sys.exit(0)
    else:
        return str(projects_home)



def validate_file_list(filelist):
    output = ""
    if len(filelist) == 1:
        output = filelist[0]
    elif len(filelist) > 1:
        print("Multiple files match your search criteria. Select the corresponding number:")
        for i, option in enumerate(filelist):
            print(f"{i}. {option}")
        choice = input("Select number: ")
        output = filelist[int(choice)]
    else:
        print("No options found. Check your input and try again.")
        sys.exit(0)
    return output








