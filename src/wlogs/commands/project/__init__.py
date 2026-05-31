from .plot import parse_plot


def parse_project(subparsers):
    project_parser = subparsers.add_parser("project")
    project_subparsers = project_parser.add_subparsers(dest="command")
    parse_plot(project_subparsers)

