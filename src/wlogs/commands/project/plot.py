import json
from pathlib import Path
import yaml
from ...config import CONFIG
from ...utils.file_lib import find_files



def get_project_root(novel_id):
    root = CONFIG["novels_path"]
    return find_files(novel_id, full_name=True, search_dir=root)


def get_wc_goal(novel_id):
    novel_path = get_project_root(novel_id)
    json_path = Path(novel_path / "novel.json")
    target = 100000
    if json_path.exists():
        with open(json_path, "r") as f:
            novel_json = json.load(f)
            target = novel_json["target_wc"]
    return target


def get_scene_header(scene_path):
    with open(scene_path, "r") as f:
        content = f.read()
        parts = content.split("---")
        yaml_str = parts[1]
        header_dict = yaml.safe_load(yaml_str)
        return header_dict


def get_all_headers(novel_id):
    scene_dir = get_project_root(novel_id) / "manuscript" / "scenes"
    scenes = list(scene_dir.rglob("*.md"))
    headers = []
    for sc in scenes:
        header = get_scene_header(sc)
        if "summary" in header:
            del header["summary"]
        headers.append(header)
    headers.sort(key=lambda h: h["scene_order"])
    return headers


def sum_chapters(scene_list) -> dict[str, int]:
    chapters = {}
    for sc in scene_list:
        cat = sc["chapter_title"].lower()
        if cat.title() not in chapters:
            chapters[cat.title()] = {}
            ch = chapters[cat.title()]
            ch["wc"] = sc["word_count"]
            ch["plotline"] = sc["protagonist"]
            ch["sequence"] = sc["scene_order"]
        else:
            chapters[cat.title()]["wc"] += sc["word_count"]
    return chapters


def get_chapter_list(chapter_counts: dict[str, int]):
    chapterlist, count = [], 0
    for key, value in chapter_counts.items():
        count += 1
        chapter = {"sequence": count, "title": key, "wc": value}
        chapterlist.append(chapter)
    return chapterlist


def calc_totals(records, target, count_prop):
    count = 0
    for sc in records:
        print(sc)
        count += sc[count_prop]
        sc["tsf"] = count
        sc["pot"] = count / target


def list_scenes(path, target, scenelist):
    csv_path = path / "scenes.csv"
    csv_str = "id,scene_id,scene_name,word_count,tsf,pot"
    calc_totals(scenelist, target, "word_count")
    for sc in scenelist:
        csv_str += f"\n{sc['scene_order']},{sc['scene_id']},{sc['scene_name']},{sc['word_count']},{sc['tsf']},{sc['pot']}"
    with open(csv_path, "w") as f:
        f.write(csv_str)


def list_chapters(target, scenelist, path):
    csv_str = "sequence,title,word_count,tsf,pot,plotline"
    csv_path = path / "chapters.csv"
    counts = sum_chapters(scenelist)
    chapters = get_chapter_list(counts)
    calc_totals(chapters, target, "wc")
    for ch in chapters:
        csv_str += (
            f"\n{ch['sequence']},{ch['title']},{ch['wc']},{ch['tsf']},{ch['pot']}"
        )
    with open(csv_path, "w") as f:
        f.write(csv_str)


def plot(args):
    novel_id = args.novel_id
    target = get_wc_goal(novel_id)
    novel_path = get_project_root(novel_id)
    scene_list = get_all_headers(novel_id)
    if args.chapters:
        list_chapters(target, scene_list, novel_path)
        print(f"Chapter list printed to {novel_path}/chapters.csv")
    else:
        list_scenes(novel_path, target, scene_list)
        print(f"Scene list printed to {novel_path}/scenes.csv")


def parse_plot(project_subparsers):
    plot_parser = project_subparsers.add_parser(
        "plot",
        help="List scenes in a table of word counts and percentages based on target total word count",
    )
    plot_parser.add_argument(
        "-id",
        "--novel_id",
        required=True,
        help="ID (i.e., folder name) of the novel whose scenes you would like to list",
    )
    plot_parser.add_argument(
        "-c",
        "--chapters",
        action="store_true",
        help="Create plotter from chapter details, instead of scenes.",
    )
    plot_parser.set_defaults(func=plot)
