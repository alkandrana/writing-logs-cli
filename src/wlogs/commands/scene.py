# Created by Rosa Lee Myers, 2026-03-14
from pathlib import Path
def new_scene(args):
    proj = args.book_id
    novel_root = f"novels/{proj}"
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
              f"summary: null\n"
              f"---\n\n"
              f"# {scene_name}\n")

    with open(f"{scene_dir}/{scene_id}.md", "w") as f:
        f.write(header)

