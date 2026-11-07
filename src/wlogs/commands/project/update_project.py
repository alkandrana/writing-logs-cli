from wlogs.library.api.crud import get_patch_payload
from wlogs.library.api.projects.update import build_project_patch, patch_goal


def update_project(args):
    payload = get_patch_payload(args.goal, "/goal")
    print("Ready to patch: ", payload)
    request = build_project_patch(payload, args.book)
    print("Patch request: ", request)
    patch_goal(request)


def parse_update_project(project_subparsers):
    update_parser = project_subparsers.add_parser("update")
    update_parser.add_argument(
        "--goal", "-g", help="The new value for the goal property"
    )
    update_parser.add_argument("--book", "-b", required=True, help="The book to update")
    update_parser.set_defaults(func=update_project)

