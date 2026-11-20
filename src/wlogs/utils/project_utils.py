import sys
from typing import Any


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
