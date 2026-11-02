from .update_project import parse_update_project
from .new_project import parse_new_project
from .count import parse_project_count
def parse_project(subparsers):
    project_parser = subparsers.add_parser("project")
    project_subparsers = project_parser.add_subparsers(dest="subcommand")
    parse_update_project(project_subparsers)
    parse_new_project(project_subparsers)
    parse_project_count(project_subparsers)