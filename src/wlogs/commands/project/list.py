import sys

import pandas as pd

from wlogs import load_config
from wlogs.library.api.auth import send_auth_request


def get_projects():
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        print(
            "There was a problem fetching records: ",
            res.status_code,
            res.reason,
            res.json(),
        )
        sys.exit(0)


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


def get_project_by_code(code):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects/code/{code}",
    }
    res = send_auth_request(request)
    return res.json()


def get_project_by_name(title):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects/name/{title}",
    }
    res = send_auth_request(request)
    return res.json()


def view_projects(args):
    if args.code:
        projects = get_project_by_code(args.code)
    elif args.title:
        projects = get_project_by_name(args.title)
    elif args.all:
        projects = get_projects()
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
