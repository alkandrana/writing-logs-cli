import os
import sys
from typing import Any

from wlogs import load_config
from wlogs.library.api.auth import send_auth_request


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
        print("Response status: ", response.status_code, response.reason, response.json())

def get_project_details(code: str) -> dict[str, Any]:
    print(f"\nAdd project details for project {code.upper()}:")
    title = input("Enter project title: ")
    series = input("Enter series title (optional): ")
    goal = input("Enter book length goal in words (default 100,000): ")
    book: dict[str, Any] = {
        "code": code.upper(),
        "title": title,
        "series": series
    }
    if not goal:
        book["goal"] = 100000
    else:
        try:
            book['goal'] = int(goal)
        except ValueError:
            print("Goal must be a valid integer.")
            sys.exit(1)
    return book

def create_project(args):
    book = get_project_details(args.code)
    post_project(book)
def parse_create_project(project_subparsers):
    create_parser = project_subparsers.add_parser("create")
    create_parser.add_argument("--code", "-c", required=True)
    create_parser.set_defaults(func=create_project)

