from ...utils.data_lib import print_options
import sys


class ProjectManager:
    def __init__(self, root):
        projects = root.rglob("novels")
        project_map = {}
        for n in projects:
            parents = list(n.parents)
            project_map[parents[0].name] = {"path": parents[0], "root": parents[1]}
            self.projects_root = parents[1]
        self.projects = project_map

    def get_novel_path(self, novel_id):
        novel_path = ""
        for key, value in self.projects.items():
            results = list(value["path"].rglob(novel_id))
            if len(results) == 1:
                novel_path = results[0]
            elif len(results) > 1:
                print("Multiple paths match your folder name. Please make a selection:")
                novel_path = print_options(results)
        if not novel_path:
            print(
                "Path to directory could not be resolved. Make sure the directory exists and try again."
            )
            sys.exit(1)
        else:
            return novel_path
