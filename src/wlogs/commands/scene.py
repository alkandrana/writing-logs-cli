# Created by Rosa Lee Myers, 2026-03-14
from pathlib import Path
from ..utils.api import *
from ..utils.file_lib import *
def new_scene(args):
    proj = args.book
    novel_root = show_projects(proj)
    # novel_data = f"{novel_root}/novel.json"
    scene_dir = f"{novel_root}/manuscript/scenes/"
    scenes_path = Path(scene_dir)
    scene_num = len([p for p in scenes_path.iterdir() if p.is_file()]) + 1

    scene_id = proj + "-" + input("Enter scene id: ")
    scene_name = input("Enter scene name: ")
    chapter = input("Enter chapter title (or enter to skip): ")
    plotline = input("Enter protagonist name: ")

    header = (f"---\n"
              f"scene_id: {scene_id}\n"
              f"scene_name: {scene_name}\n"
              f"chapter_title: {chapter}\n"
              f"scene_order: {scene_num}\n"
              f"protagonist: {plotline}\n"
              f"status: draft\n"
              f"word_count: 0\n"
              "summary: {\n"
              "  Input: The state of the characters at the beginning of the scene.\n"
              "  Process: What happens in the scene.\n"
              "  Output: The change in the state of the story by the end of the scene.\n"
              "}\n"
              f"---\n\n"
              f"# {scene_name}\n")

    with open(f"{scene_dir}/{scene_id}.md", "w") as f:
        f.write(header)

def cmd_update_scene_status(args):
    status = args.status
    if status == "finished":
        summarize = input("Add a summary? (y/n): ")
        if summarize == "y":
            book_id = input("Enter project id: ")
            update_scene_data(book_id, args.scene)
    payload = {
        "status": status
    }
    updated = send_patch_request(payload, f"scenes/{args.scene}")
    print(f"Updated scene status for {args.scene}: {updated['status']}")
    print(updated)

def parse_scene(subparsers):
    scene_parser = subparsers.add_parser("scene")
    scene_subparsers = scene_parser.add_subparsers(dest="command")
    update_parser = scene_subparsers.add_parser("update", help="Update scene details")
    update_parser.add_argument("--scene", required=True, help="Scene code")
    update_parser.add_argument("--status", required=True, help="Scene status")
    update_parser.set_defaults(func=cmd_update_scene_status)

    create_parser = scene_subparsers.add_parser("create", help="Create new scene file with yaml header.")
    create_parser.add_argument("--book", required=True, help="ID of the novel in whic to create the scene (e.g., SOD)")
    create_parser.set_defaults(func=new_scene)
