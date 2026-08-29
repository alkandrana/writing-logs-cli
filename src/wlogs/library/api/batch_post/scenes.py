import sys
from pathlib import Path
from .utils import transfer, post_record
from wlogs.library.api.crud import get_status_values
from wlogs.library.file.scenes import load_yaml_header
from wlogs.library.file.search import find_file, fast_search
from ..projects.list import get_project_by_id
from ....commands import get_project_id

node_url = 'http://localhost:3000'
def translate_status(status):
    statuses = get_status_values()
    if status == "written":
        value = "finished"
    elif status == "draft":
        value = "writing"
    elif status == "archive":
        value = "aborted"
    else:
        value = status
    status_id = [st["id"] for st in statuses if st["name"] == value][0]
    return status_id

def build_scene_from_file(scene_header, project_id):
    statuses = get_status_values()
    status_id = translate_status(scene_header['status'])
    if status_id == 0:
        status_id = [st["id"] for st in statuses if st["name"] == "pending"][0]
    code_parts = scene_header["scene_id"].split("-")
    scene_code = code_parts[1] if len(code_parts) == 2 else code_parts[0]
    plotline = ""
    for key in scene_header.keys():
        if "protagonist" in key:
            plotline = scene_header[key]
    try:
        scene = {
            "code": scene_code,
            "sequence": scene_header["scene_order"],
            "name": scene_header["scene_name"],
            "words": scene_header["word_count"],
            "statusId": status_id,
            "plotline": plotline,
            "projectId": project_id,
        }
        return scene
    except KeyError:
        print(f"Malformed scene header for scene: {scene_header}")
        return {}


def get_scene_details(book_code):
    # check whether project exists
    project_id = get_project_id(book_code)
    if not project_id:
        print("Project doesn't exist yet. Create it with 'wlogs projects create', or create all missing projects with 'wlogs batch projects -s file'")
        sys.exit(1)
    print(f"\nLocating repo for project {book_code}")
    path = find_file(book_code.upper())
    scenes_path = Path(path) / "manuscript" / "scenes"
    print(scenes_path)
    if not scenes_path.exists():
        print("Malformed project repo. Makes sure your project tree follows the pattern: root/books/<book_ID>/manuscript/scenes")
        sys.exit(1)
    scenes = [p for p in fast_search(".md", scenes_path)]
    batch = []
    for path in scenes:
        print(f"\nGetting post details for scene: {path.name}")
        header = load_yaml_header(path)
        if not isinstance(header, dict) or not header:
            print(f"Malformed scene header or header not present: {path}. Skipping...")
        else:
            payload = build_scene_from_file(header, project_id)
            if not payload:
                print("Scene details could not be determined. Skipping scene...")
            else:
                batch.append(payload)
    batch.sort(key=lambda x: x["sequence"])
    return batch


def get_project_relation(sc):
    req = {
        "method": "GET",
        "endpoint": f"{node_url}/projects/{sc['projectId']}",
    }
    code = get_project_by_id(req)
    project_id = get_project_id(code)
    return project_id


def format_scenes(scenes):
    statuses = get_status_values()
    scenelist = []
    for s in scenes:
        scene = {
            "code": s["code"],
            "sequence": s["sequence"],
            "name": s["name"],
            "words": s["words"],
            "statusId": [st["id"] for st in statuses if st["name"] == s["status"]][0],
            "plotline": s["plotline"],
            "projectId": get_project_relation(s),
        }
        scenelist.append(scene)
    return scenelist


def batch_scenes(args):
    if args.source == "api":
        transfer(node_url, "scenes", format_scenes)
    elif args.source == "file":
        scenes_to_post = get_scene_details(args.code)
        for sc in scenes_to_post:
            post_record(sc, "scenes")
    else:
        print("Source must be one of 'api' or 'file'")
        sys.exit(1)


def parse_batch_scenes(batch_subparsers):
    scene_parser = batch_subparsers.add_parser("scenes")
    scene_parser.add_argument("--source", "-s", required=True)
    scene_parser.add_argument("--code", "-c", required=True)
    scene_parser.set_defaults(func=batch_scenes)
