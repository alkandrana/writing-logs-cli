import sys

import pandas as pd

from wlogs.utils.crud import get_all_records, get_record_by_code, get_record_by_name


def print_projects(projects):
    if len(projects) > 0:
        print(f"\nFound {len(projects)} projects:\n")
        project_list: list[dict[str, str | int]] = [
            {
                "code": proj["code"],
                "title": proj["title"],
                "series": proj["series"],
                "goal": proj["goal"],
            }
            for proj in projects
        ]
        dataframe = pd.DataFrame(project_list)
        print(dataframe)
        print()
    else:
        print("\nNo projects found matching that criterion.\n")


def view_projects(args):
    if args.code:
        projects = [get_record_by_code(args.code, "projects")]
    elif args.title:
        projects = get_record_by_name(args.title, "projects")
    elif args.all:
        projects = get_all_records("projects")
    else:
        print(
            "No search criterion submitted. See 'wlogs project list --help' for more information."
        )
        sys.exit(1)
    print_projects(projects)


def parse_project_list(project_subparsers):
    list_parser = project_subparsers.add_parser("list")
    list_parser.add_argument(
        "--code", "-c", required=False, help="Get a project by its code (e.g., SOD)"
    )
    list_parser.add_argument("--title", "-t", required=False)
    list_parser.add_argument("--all", "-a", action="store_true", required=False)
    list_parser.set_defaults(func=view_projects)
