import sys, os, re, json
from pathlib import Path
from typing import Any
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


def find_files(keyword, target=Path.home(), full_name=False) -> Path | None:
    options = []
    for path in fast_search(keyword, target_dir=target, full_name=full_name):
        options.append(path)
    if len(options) > 1:
        choice = print_options(options)
    elif len(options) == 1:
        choice = options[0]
    else:
        print(f"No files matched your search.")
        return None
    return choice

# fast alternative to find_files with rglob
# returns a function generator object; either use a for loop on the call, or next() on the result
def fast_search(target_filename, target_dir: Path | str = Path.home(), full_name: bool = False):
    # os.scandir returns an iterator that points directly to system memory
    for entry in os.scandir(target_dir):
        if not entry.name.startswith(".") and not entry.name == "Library":
            condition = target_filename == entry.name if full_name else target_filename in entry.name
            if condition:
                yield Path(entry.path)
            elif entry.is_dir(follow_symlinks=False):
                # Recurse into subdirectories
                try:
                    yield from fast_search(target_filename, target_dir=entry.path, full_name=full_name)
                except PermissionError:
                    continue

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
