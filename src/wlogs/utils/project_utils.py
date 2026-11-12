import sys
from typing import Any

from requests import JSONDecodeError

from wlogs import load_config
from wlogs.commands.auth import send_auth_request

from .crud import get_record_id


def get_project_details(code: str) -> dict[str, Any]:
    print(f"\nAdd project details for project {code.upper()}:")
    title = input("Enter project title: ")
    series = input("Enter series title (optional): ")
    goal = input("Enter book length goal in words (default 100,000): ")
    book: dict[str, Any] = {"code": code.upper(), "title": title, "series": series}
    if not goal:
        book["goal"] = 100000
    else:
        try:
            book["goal"] = int(goal)
        except ValueError:
            print("Goal must be a valid integer.")
            sys.exit(1)
    return book


def get_project_id(project_code: str) -> int | None:
    options = get_record_id(project_code, "projects")
    if options:
        project = options[0]
        pid = int(project["id"]) if project["id"] else 0
        return pid


def post_project(book):
    request = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/projects",
        "payload": book,
    }
    response = send_auth_request(request)
    if response.status_code == 409:
        print("Project already exists. Skipping...")
    elif 200 <= response.status_code < 300:
        print("Project successfully created.")
    else:
        print(
            "Response status: ", response.status_code, response.reason, response.json()
        )


def build_project_patch(payload, project_code):
    project_id = get_project_id(project_code)
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/projects/{project_id}",
        "payload": payload,
    }
    return request


def patch_project(request):
    res = send_auth_request(request)
    if not 200 <= res.status_code < 300:
        print("An error occured: ", res.status_code, res.reason, res.json())
        sys.exit(1)
    else:
        print("Successfully updated goal")


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


def get_project_by_code(code):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects/code/{code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()[0]
    elif res.status_code == 404:
        print("No projects found matching that code.")
        sys.exit(1)
    else:
        print(f"An error occurred: {res.status_code}: {res.reason}")
        try:
            print(f"Details: {res.json()}")
        except JSONDecodeError:
            print("Details: No error message returned.")
        sys.exit(1)


def get_project_by_id(pid):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects/{pid}",
    }
    res = send_auth_request(request)
    return res.json()
