import sys

import pandas as pd

from wlogs.utils.crud import get_record_by_code, get_record_by_name
from wlogs.utils.scene_utils import get_scenes_by_project


def print_scene(scenelist):
    scenelist = [
        {
            "code": sc["code"],
            "sequence": sc["sequence"],
            "name": sc["name"],
            "chapter": sc["chapter"] if sc["chapter"] else "",
            "words": sc["words"],
            "status": sc["status"]["name"] if sc["status"] else "",
            "plotline": sc["plotline"] if sc["plotline"] else "",
            "project": sc["project"]["title"] if sc["project"] else "",
        }
        for sc in scenelist
    ]
    df = pd.DataFrame(scenelist)
    print(df)


def view_one_scene(args):
    if args.code:
        criterion = f"code {args.code}"
        scenes = get_record_by_code(args.code, "scenes")
    elif args.name:
        criterion = f"name {args.name}"
        scenes = get_record_by_name(args.name, "scenes")
    elif args.project:
        criterion = f"project {args.project}"
        scenes = get_scenes_by_project(args.project)
    else:
        print("No search key submitted.")
        sys.exit(1)
    print(f"\n{len(scenes)} scenes match {criterion}:\n")
    print_scene(scenes)


def parse_list_scenes(scene_subparsers):
    list_parser = scene_subparsers.add_parser("list")
    list_parser.add_argument("--code", "-c", required=False)
    list_parser.add_argument("--project", "-p", required=False)
    list_parser.add_argument("--name", "-n", required=False)
    list_parser.set_defaults(func=view_one_scene)
