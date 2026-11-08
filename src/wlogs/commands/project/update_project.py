from wlogs.library.api.crud import get_patch_payload
from wlogs.library.api.projects.update import build_project_patch, patch_goal


def update_project(args):
    payload = []
    if args.goal:
        payload.append(get_patch_payload(args.goal, "/goal"))
    elif args.series:
        payload.append(get_patch_payload(args.series, "/series"))
    elif args.title:
        payload.append(get_patch_payload(args.title, "/title"))
    print("Ready to patch: ", payload)
    request = build_project_patch(payload, args.book)
    print("Patch request: ", request)
    c = input("Proceed with update? (y/n): ")
    if c.lower() == "y":
        patch_goal(request)


def parse_update_project(project_subparsers):
    update_parser = project_subparsers.add_parser("update")
    update_parser.add_argument(
        "--goal", "-g", help="The new value for the goal property"
    )
    update_parser.add_argument(
        "--series", "-s", required=False, help="New value for the series title"
    )
    update_parser.add_argument(
        "--title", "-t", required=False, help="New value for the book title"
    )
    update_parser.add_argument("--book", "-b", required=True, help="The book to update")
    update_parser.set_defaults(func=update_project)
