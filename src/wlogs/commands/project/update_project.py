from wlogs.utils.crud import build_patch, get_record_id, send_update_request


def update_project(args):
    payload = []
    project_id = get_record_id(args.code, "projects")
    if args.goal:
        payload.append(build_patch("goal", args.goal))
    elif args.series:
        payload.append(build_patch("/series", args.series))
    elif args.title:
        payload.append(build_patch("/title", args.title))
    print("Ready to patch: ", payload)
    print("Patch request: ", payload)
    c = input("Proceed with update? (y/n): ")
    if c.lower() == "y":
        send_update_request(payload, "projects", project_id)


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
