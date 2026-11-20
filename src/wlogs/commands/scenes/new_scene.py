import sys

from wlogs.utils.crud import (
    check_record_exists,
    get_all_records,
    get_record_id,
    post_record,
)


def get_scene_details(scene):
    print(f"\nAdd details for scene {scene['code']}: ")
    name = input("Enter scene name/description: ")
    sequence = input(
        "Enter scene number (where in the story the scene falls; optional): "
    )
    words = input("Enter word count for scene: ")
    status = input(
        "Enter scene status (pending, writing, finished, aborted; default pending): "
    )
    plotline = input("Enter name of POV character for this scene (optional): ")
    chapter = input("Enter chapter title (optional): ")
    scene["name"] = name
    scene["plotline"] = plotline
    scene["chapter"] = chapter
    try:
        scene["sequence"] = int(sequence) if sequence else 0
        scene["words"] = int(words) if words else 0
    except ValueError:
        print("Scene number and words must be valid integers")
        sys.exit(1)
    scene["statusId"] = get_record_id(status, "status", "name")


def get_scene_codes(code: str):
    if "-" in code:
        project = code[0 : code.index("-")]
        scene_code = code
    else:
        project_list = get_all_records("projects")
        print("Scene project could not be determined.")
        if len(project_list) > 0:
            for i, project in enumerate(project_list):
                print(f"{i}. {project['code']}: {project['title']}")
            choice = input("Select the corresponding number: ")
            project = project_list[int(choice)]["code"]
            scene_code = f"{project}-{code}"
        else:
            print(
                "No projects found. Create one with 'wlogs project add -c <project_code>'"
            )
            sys.exit(1)
    return {"project": project, "scene": scene_code}


def create_scene(args):
    code = args.code
    codes = get_scene_codes(code)
    if not check_record_exists(codes["project"], "projects"):
        print(
            f"Scene's project does not exist. Create it with 'wlogs projects create -c {codes['project']}'"
        )
        sys.exit(1)
    project_id = get_record_id(codes["project"], "projects")
    scene = {"code": codes["scene"], "projectId": project_id}
    get_scene_details(scene)
    post_record(scene, "scenes")


def parse_new_scene(scenes_subparsers):
    create_parser = scenes_subparsers.add_parser("add")
    create_parser.add_argument("--code", "-c", required=True)
    create_parser.set_defaults(func=create_scene)
