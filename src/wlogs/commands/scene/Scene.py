from typing import Any
import yaml
import json
import sys

from ...utils.api import Api
from ...utils.file_lib import find_files
from ...config import CONFIG

API = Api()
class Scene:
    def __init__(self, scene_id) -> None:
        print(f"Initializing Scene object for {scene_id}")
        self.novel_id = scene_id.split("-")[0]
        self.scene_id = scene_id.split("-")[1]
        self.novel = find_files(self.novel_id, search_dir=CONFIG["novels_path"], full_name=True)
        self.scene = find_files(self.scene_id, search_dir=self.novel)
        self.header = self.get_yaml_header()

    # def validate_projects_root(self):
    #     for key in self.projects:
    #         if self.projects[key]["root"] != self.projects_root:
    #             return False
    #     return True

    # def show_projects(self, project: str):
    # novel_root = self.projects[project]["path"]

    # def get_scene_json(self, book_id: str, scene_id: str):
    #     header_dict = self.get_yaml_header(scene_id)
    #     print(header_dict)
    #     self.add_yaml_summary(header_dict)
    #     print(header_dict)
    #     self.write_json_header(header_dict, book_id)

    def get_yaml_header(self) -> dict[str, Any]:
        with open(self.scene, "r") as f:
            content = f.read()
        parts = content.split("---")
        yaml_str = parts[1]
        header_dict = yaml.safe_load(yaml_str)
        return header_dict

    def add_yaml_summary(self):
        for key, value in self.header.items():
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

    def write_json_header(self):
        json_path = self.novel / "novel.json"
        if json_path.exists():
            with open(json_path, "r") as f:
                novel_dict = json.load(f)
        else:
            novel_dict = {
                "book_id": self.novel_id,
                "title": "",
                "volume": 0,
                "structure": "",
                "target_wc": 100000,
                "status": "draft",
                "summary": "",
                "scenes": [],
            }
        print(novel_dict)
        if "scenes" in novel_dict:
            novel_dict["scenes"].append(self.header)
        else:
            novel_dict["scenes"] = [self.header]
        with open(json_path, "w") as f:
            json.dump(novel_dict, f, indent=2, sort_keys=True)

    def get_scene_id(self) -> int|None:
        scene = API.get_results(self.scene_id, "scenes/code")
        if scene:
            return scene["id"]
        else:
            print(f"No scene with code {self.scene_id} found. Create it with 'wlogs scene new'", file=sys.stderr)
            sys.exit(1)

    def get_project_id(self) -> int:
        project = API.get_one_record(self.novel_id, "projects/code")
        if project:
            return project["id"]
        else:
            print(f"No project with code {self.novel_id} found. Create it with 'wlogs project new'", file=sys.stderr)
            sys.exit(1)