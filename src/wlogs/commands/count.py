# Created by Rosa Lee Myers, 2026-02-22
# Assumes an .md scene file with a yaml header
import re
from pathlib import Path
def count_scene(filename):
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
