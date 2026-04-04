import sys
from pathlib import Path
from typing import Any
import json
import yaml

ROOT_DIR = "/Users/rosamyers/repos"
def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def save_state(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def clear_state(path: Path) -> None:
    if path.exists():
        path.unlink()

def get_novel_directory():
    projects_home = Path(Path.home() / ROOT_DIR)
    if not projects_home.exists():
        print("Could not resolve root directory. Make sure directory is in home folder and try again.")
        sys.exit(0)
    else:
        return str(projects_home)

def show_projects(project: str) -> str:
    novel_dir = get_novel_directory()
    projects = [f for f in Path(novel_dir).rglob(project) if f.is_dir() and "novels" in str(f.parent)]
    if len(projects) == 1:
        return str(projects[0])
    elif len(projects) > 1:
        print("Multiple novels match your search criteria. Select the corresponding number:")
        for i, project in enumerate(projects):
            print(f"{i}. {project}")
        choice = input("Select number: ")
        return str(projects[int(choice)])
    else:
        print("No projects found. Check your project designation and try again.")
        sys.exit(0)

def validate_file_list(path, filename, message):
    options = [f for f in Path(path).rglob("*" + filename + "*")]
    output = ""
    if len(options) == 1:
        output = options[0]
    elif len(options) > 1:
        print(f"{message} Select the corresponding number:")
        for i, option in enumerate(options):
            print(f"{i}. {option}")
        choice = input("Select number: ")
        output = options[int(choice)]
    else:
        print("No options found. Check your input and try again.")
        sys.exit(0)
    return output

def list_scenes(scene_code):
    scene = validate_file_list(ROOT_DIR, scene_code, f"Multiple scenes match your search criteria.")
    return scene
def count_scene(scene_code: str) -> int:
    scene_path = list_scenes(scene_code)
    with open(scene_path, "r") as f:
        content = f.read()
        parts = content.split("---")
        header = parts[1]
        header_dict = yaml.safe_load(header)
    return header_dict["word_count"]

