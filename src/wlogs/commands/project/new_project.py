import sys
from pathlib import Path

from wlogs import load_config

# from ...library.file.projects.new_project import create_book_structure
from ...library.api.projects.create import post_project


# get input from user
def create_new_project(args):
    name = args.name
    novel_home = Path(load_config()["novel_home"])
    if novel_home.exists():
        print("Creating new project directory...")
        new_proj = novel_home / name
        new_proj.mkdir(parents=True, exist_ok=True)
        print("Creating books directory...")
        (new_proj / "books").mkdir(parents=True, exist_ok=True)
        print("Creating README stub...")
        (new_proj / "README.md").touch()
        choice = input("Add optional description? (y/n): ")
        if choice == "y":
            description = input("Enter description: ")
        else:
            description = ""
        with open(new_proj / "README.md", "w") as f:
            f.write(f"# {name}\n{description}")
        print(f"Project structure created for {name}")
    else:
        print("Novel home missing or out of date. Update it with 'wlogs config novel'")
        sys.exit(1)


def add_new_book(args):
    book = {}
    # book = create_book_structure(args.code, args.project)
    # post_project(book)


def parse_new_project(project_subparsers):
    create_parser = project_subparsers.add_parser("create")
    create_parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="Name of the new project. This will be used as the directory name, as well.",
    )
    create_parser.set_defaults(func=create_new_project)

    book_parser = project_subparsers.add_parser("add")
    book_parser.add_argument(
        "--code", "-c", required=True, help="Code for the new book."
    )
    book_parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="(Directory) name of the project in which to create the book",
    )
    book_parser.set_defaults(func=add_new_book)
