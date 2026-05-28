from typing import Any
import yaml
import json
from ...config import HOME_DIR
from ...utils.file_lib import find_files


class SceneManager:
    def __init__(self, root) -> None:
        self.root_dir = root
        novels = list(HOME_DIR.rglob("novels"))
        project_map = {}
        for n in novels:
            parents = list(n.parents)
            project_map[parents[0].name] = {"path": parents[0], "root": parents[1]}
            self.projects_root = parents[1]
        self.projects = project_map

    def validate_projects_root(self):
        for key in self.projects:
            if self.projects[key]["root"] != self.projects_root:
                return False
        return True

    # def show_projects(self, project: str):
    # novel_root = self.projects[project]["path"]

    # def get_scene_json(self, book_id: str, scene_id: str):
    #     header_dict = self.get_yaml_header(scene_id)
    #     print(header_dict)
    #     self.add_yaml_summary(header_dict)
    #     print(header_dict)
    #     self.write_json_header(header_dict, book_id)

    def get_yaml_header(self, scene_code: str) -> dict[str, Any]:
        scene_path = find_files(scene_code)
        with open(scene_path, "r") as f:
            content = f.read()
        parts = content.split("---")
        yaml_str = parts[1]
        header_dict = yaml.safe_load(yaml_str)
        return header_dict

    def add_yaml_summary(self, yaml_header: dict[str, Any]):
        for key, value in yaml_header.items():
            if not value and key == "summary":
                input_prop = input(
                    "Input (the state of the characters at the beginning of the scene): "
                )
                process_prop = input("Process (what happens in the scene): ")
                output_prop = input(
                    "Output (the change in the 'state' of the story by the end of the scene): "
                )
                value = {
                    "Input": input_prop,
                    "Process": process_prop,
                    "Output": output_prop,
                }

    def write_json_header(self, yaml_header, novel_id):
        novel_path = find_files(novel_id)
        json_path = novel_path[0] / "novel.json"
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
                "scenes": [],
            }
        novel_dict["scenes"].append(yaml_header)
        with open(json_path, "w") as f:
            json.dump(novel_dict, f, indent=2, sort_keys=True)
