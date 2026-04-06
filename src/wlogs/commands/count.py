# Created by Rosa Lee Myers, 2026-02-22
# Assumes an .md scene file with a yaml header
import re
from ..utils.file_lib import *
from ..utils.api import send_patch_request

def count_words(filename):
    pattern = r'\b[a-zA-z-\'’]\b'
    with open(filename) as f:
        count = 0
        text = ""
        for line in f:
            if line[0:3] == "---":
                count += 1
            if count == 2 and line[0] != '#':
                text += line
    words = re.findall(pattern, text)
    return len(words)

def find_file(key, root):
    search_dir = Path.home()
    if root:
        search_dir = search_dir / root
        print(f"Search directory: {search_dir}")
    file_list = list(search_dir.rglob(f'{key}'))
    if len(file_list) == 1:
        return file_list[0]
    else:
        return file_list

def get_scene(key, root, scene):
    scene_area = find_file(key, root)
    scene = find_file(scene, scene_area)
    return scene

def cmd_update_scene_count(args):
    header = get_yaml_header(args.scene)
    word_count = header["word_count"]
    payload = {
        "words": word_count
    }
    updated = send_patch_request(payload, f"scenes/{args.scene}")
    print(f"Updated scene count for {args.scene}: {payload['words']}")
    print(updated)

def count_parser(subparsers):
    count_parser = subparsers.add_parser("count")
    count_subparsers = count_parser.add_subparsers(dest="command")
    scene_parser = count_subparsers.add_parser("scene", help="Update word count for a scene")
    scene_parser.add_argument("--scene", required=True, help="Scene code (e.g., DGP-DBT")
    scene_parser.set_defaults(func=cmd_update_scene_count)