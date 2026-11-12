from .count import parse_project_count
from .list import parse_project_list
from .new_project import parse_new_project
from .update_project import parse_update_project


def parse_project(subparsers):
    project_parser = subparsers.add_parser("project")
    project_subparsers = project_parser.add_subparsers(dest="subcommand")
    parse_update_project(project_subparsers)
    parse_new_project(project_subparsers)
    parse_project_count(project_subparsers)
    parse_project_list(project_subparsers)
