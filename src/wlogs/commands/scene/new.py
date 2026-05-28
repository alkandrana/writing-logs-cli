from pathlib import Path
from typing import Any, Dict

from wlogs.config import HOME_DIR
from wlogs.utils.file_lib import find_files
from .scene_manager import SceneManager

scene_mng = SceneManager(HOME_DIR)


def get_scene_dir(args) -> Path:
    proj = args.book
    novel_root = find_files(proj)
    # novel_data = f"{novel_root}/novel.json"
    scene_dir = f"{novel_root}/manuscript/scenes/"
    return Path(scene_dir)


def get_scene_details(args, scene_path) -> Dict[str, Any]:
    return {
        "scene_num": (len([p for p in scene_path.iterdir() if p.is_file()]) + 1),
        "scene_id": args.book + "-" + input("Enter scene id: "),
        "scene_name": input("Enter scene name: "),
        "chapter": input("Enter chapter title (or enter to skip): "),
        "plotline": input("Enter protagonist name: "),
    }


def build_yaml_header(deets: Dict[str, Any]) -> str:
    return (
        f"---\n"
        f"scene_id: {deets['scene_id']}\n"
        f"scene_name: {deets['scene_name']}\n"
        f"chapter_title: {deets['chapter']}\n"
        f"scene_order: {deets['scene_num']}\n"
        f"protagonist: {deets['plotline']}\n"
        f"status: draft\n"
        f"word_count: 0\n"
        "summary: {\n"
        "  Input: The state of the characters at the beginning of the scene.\n"
        "  Process: What happens in the scene.\n"
        "  Output: The change in the state of the story by the end of the scene.\n"
        "}\n"
        f"---\n\n"
        f"# {deets['scene_name']}\n"
    )


def new_scene(args):
    ### Get directory where scene will be created ###
    scene_path = get_scene_dir(args)
    ### Get properties for yaml header ###
    scene_details = get_scene_details(args, scene_path)
    ### build yaml header ###
    header = build_yaml_header(scene_details)
    ### Create file and print header ###
    with open(f"{scene_path}/{scene_details['scene_id']}.md", "w") as f:
        f.write(header)


def parse_new_scene(scene_subparsers):
    create_parser = scene_subparsers.add_parser(
        "create", help="Create new scene file with yaml header."
    )
    create_parser.add_argument(
        "--book",
        required=True,
        help="ID of the novel in which to create the scene (e.g., SOD)",
    )
    create_parser.set_defaults(func=new_scene)
