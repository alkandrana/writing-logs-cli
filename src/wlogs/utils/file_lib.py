import sys
from pathlib import Path
from typing import Any
import json
import yaml
from wlogs.config import state_path

ROOT_DIR = Path.home() / "repos"

def load_session_data():
    path = state_path()
    if path.exists():
        with open(path, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    return data

def session_in_progress():
    if load_session_data():
        return True
    else:
        return False
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

def list_scenes(scene_code):
    files = [f for f in Path(ROOT_DIR).rglob(f"*{scene_code}*")]
    scene_path = validate_file_list(files)
    return scene_path
def get_yaml_header(scene_code: str) -> dict[str, Any]:
    scene_path = list_scenes(scene_code)
    with open(scene_path, "r") as f:
        content = f.read()
    parts = content.split("---")
    yaml_str = parts[1]
    header_dict = yaml.safe_load(yaml_str)
    return header_dict

def convert_to_json(yaml_header, novel_id):
    options = [f for f in Path(ROOT_DIR).rglob(novel_id)]
    novel_path = validate_file_list(options)
    json_path = Path(novel_path / "novel.json")
    if json_path.exists():
        with open(json_path, "r") as f:
            novel_dict = json.load(f)
    else:
        novel_dict = {
            "book_id": novel_id,
            "title": "",
            "volume": 0,
            "structure": "",
            "target_wc": 100000,
            "status": "draft",
            "summary": "",
            "scenes": []
        }
    novel_dict["scenes"].append(yaml_header)
    with open(json_path, "w") as f:
        json.dump(novel_dict, f, indent=2, sort_keys=True)

def validate_yaml_header(yaml_header: dict[str, Any]):
    for key, value in yaml_header.items():
        if not yaml_header[key] and key == "summary":
            input_prop = input("Input (the state of the characters at the beginning of the scene): ")
            process_prop = input("Process (what happens in the scene): ")
            output_prop = input("Output (the change in the 'state' of the story by the end of the scene): ")
            yaml_header[key] = {
                "Input": input_prop,
                "Process": process_prop,
                "Output": output_prop
            }

def update_scene_data(book_id: str, scene_id: str):
    header_dict = get_yaml_header(scene_id)
    print(header_dict)
    validate_yaml_header(header_dict)
    print(header_dict)
    convert_to_json(header_dict, book_id)