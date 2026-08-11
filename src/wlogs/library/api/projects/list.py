import os, dotenv

from wlogs import load_config
from wlogs.library.api.auth import send_auth_request
from wlogs.commands import node_url, send_request

dotenv.load_dotenv()


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


def print_projects(projects):
    print(f"Found {len(projects)} projects:\n")
    for rec in projects:
        for key, value in rec.items():
            if "author" not in key:
                print(f"{key}: {value}")
            elif key == "author":
                print(f"{key}: {value['userName']}")
        print("\n")


def view_all(args):
    projects = get_projects()
    print_projects(projects)


def get_project_by_code(code):
    request = {
        "method": "GET",
        "endpoint": f"{os.getenv('BASE_URL')}/projects/code/{code}",
    }
    res = send_auth_request(request)
    return res.json()[0]


def get_project_by_id(pid):
    request = {
        "method": "GET",
        "endpoint": f"{os.getenv('BASE_URL')}/projects/{pid}",
    }
    res = send_auth_request(request)
    return res.json()


def print_project(project):
    print(f"\nProject {project['id']}: {project['title']}")
    for key, value in project.items():
        if "author" not in key:
            print(f"{key}: {value}")
    print("\n")


def view_one(args):
    project = get_project_by_code(args.code)
    print_project(project)


# def get_project_by_id(request, getter):
#     res = getter(request)
#     if 200 <= res.status_code < 300:
#         return res.json()['code']
#     else:
#         print("An error occurred: ", res.status_code, res.reason)
#         sys.exit(1)


def get_project_code(args):
    project_id = args.id
    request = {
        "method": "GET",
        "endpoint": f"{node_url}/projects/{project_id}",
    }
    code = get_project_by_id(request, send_request)
    print(f"Project {project_id}: {code}")


def parse_project_list(project_subparsers):
    list_parser = project_subparsers.add_parser("list")
    list_subparsers = list_parser.add_subparsers(dest="sub2command")
    code_parser = list_subparsers.add_parser("code")
    code_parser.add_argument("--id", required=True)
    code_parser.set_defaults(func=get_project_code)

    all_parser = list_subparsers.add_parser("all")
    all_parser.set_defaults(func=view_all)

    one_parser = list_subparsers.add_parser("one")
    one_parser.add_argument("--code", "-c", required=True)
    one_parser.set_defaults(func=view_one)
