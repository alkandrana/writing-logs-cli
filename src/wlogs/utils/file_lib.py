import sys
from pathlib import Path
from typing import Any
import json
from ..config import HOME_DIR
from .data_lib import print_options


# NOVEL_ROOT = get_novel_parent()
def get_last_line(path):
    with open(path, "r") as f:
        last_line = ""
        for line in f:
            if line.strip():
                last_line = line
    if last_line:
        return last_line
    else:
        print("No data found.")
        sys.exit(0)


def find_files(file_name: str):
    options = [f for f in Path(HOME_DIR).rglob(file_name)]
    if len(options) > 1:
        choice = print_options(options)
    elif len(options) == 1:
        choice = options[0]
    else:
        print("No files matched your search criteria.")
        sys.exit(1)
    return choice


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_json_to_file(path: Path, data: dict[str, Any]):
    with open(path, "w") as f:
        json.dump(data, f)


def validate_file_list(filelist):
    output = ""
    if len(filelist) == 1:
        output = filelist[0]
    elif len(filelist) > 1:
        print(
            "Multiple files match your search criteria. Select the corresponding number:"
        )
        for i, option in enumerate(filelist):
            print(f"{i}. {option}")
        choice = input("Select number: ")
        output = filelist[int(choice)]
    else:
        print("No options found. Check your input and try again.")
        sys.exit(0)
    return output
