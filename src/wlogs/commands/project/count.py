from wlogs.library.api.scenes.scenes_by_project import get_scenes

def get_project_words(code):
    proj = get_scenes(code)
    scenes = proj["scenelist"]
    total_words = sum(scene.get("words", 0) for scene in scenes)
    return total_words

def print_project_word_count(args):
    total_words = get_project_words(args.code)
    print(f"\nProject {args.code} has a total of {total_words:,} words.\n")

def parse_project_count(project_subparsers):
    count_parser = project_subparsers.add_parser("count")
    count_parser.add_argument("--code", "-c", required=True, help="Project Code")
    count_parser.set_defaults(func=print_project_word_count)