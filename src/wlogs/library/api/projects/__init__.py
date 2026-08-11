from .list import parse_project_list
from .create import parse_create_project
def parse_projects(subparsers):
    project_parser = subparsers.add_parser("projects")
    project_subparsers = project_parser.add_subparsers(dest="subcommand")
    parse_project_list(project_subparsers)
    parse_create_project(project_subparsers)