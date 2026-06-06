import re
from wlogs.config import CONFIG
from wlogs.utils.file_lib import find_files


def count_words_in_scene(scene_path):
    pattern = r"\b[a-zA-z-\'’]\b"
    with open(scene_path) as f:
        count = 0
        text = ""
        for line in f:
            if line[0:3] == "---":
                count += 1
            if count == 2 and line[0] != "#":
                text += line
    words = re.findall(pattern, text)
    return len(words)


def get_scene_count(args):
    novels_dir = CONFIG["novels_path"]
    scene_path = find_files(args.code, search_dir=novels_dir)
    word_count = count_words_in_scene(scene_path)
    print(f"There are {word_count} words in {args.code}")


def parse_count_scene(count_subparsers):
    scene_parser = count_subparsers.add_parser(
        "scene", help="Count words in a scene file"
    )
    scene_parser.add_argument("--code", required=True, help="Scene code")
    scene_parser.set_defaults(func=get_scene_count)
