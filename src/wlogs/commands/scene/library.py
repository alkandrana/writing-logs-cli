from pathlib import Path
import sys
from typing import Any
import yaml
import json
from ...config import HOME_DIR
from ...utils.file_lib import validate_file_list
def show_projects(project_id: str) -> str:
    projects = [f for f in HOME_DIR.rglob(project_id) if f.is_dir() and "novels" in str(f.parent)]
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

def update_scene_data(book_id: str, scene_id: str):
    header_dict = get_yaml_header(scene_id)
    print(header_dict)
    validate_yaml_header(header_dict)
    print(header_dict)
    convert_to_json(header_dict, book_id)

def get_yaml_header(scene_code: str) -> dict[str, Any]:
    scene_path = list_scenes(scene_code)
    with open(scene_path, "r") as f:
        content = f.read()
    parts = content.split("---")
    yaml_str = parts[1]
    header_dict = yaml.safe_load(yaml_str)
    return header_dict

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
def convert_to_json(yaml_header, novel_id):
    options = [f for f in Path(Path.home() / "repos").rglob(novel_id)]
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

def list_scenes(scene_code):
    files = [f for f in Path(get_novel_parent()).rglob(f"*{scene_code}*")]
    scene_path = validate_file_list(files)
    return scene_path

def get_novel_parent():
    novels = [f for f in HOME_DIR.rglob("novels")]
    parents = [f for f in novels[0].parents]
    novel_parent = parents[1]
    for n in novels:
        parents = [f for f in n.parents]
        if novel_parent != parents[1]:
            print("Novel path is not universal")
            sys.exit(0)
    return novel_parent
