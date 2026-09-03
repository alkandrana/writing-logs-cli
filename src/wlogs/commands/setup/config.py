import json, sys
from wlogs.library.file.search import find_file
from ... import get_store_path
from wlogs.library.api.auth import check_server_health


def set_log_file(_):
    log = input("Enter the name of your writing sessions log file: ")
    log_path = find_file(log)
    config_path = get_store_path()
    config_file = config_path / "config.json"
    if log_path.exists():
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
            config["log_file"] = str(log_path)
        else:
            config = {"log_file": str(log_path)}
            config_path.mkdir(parents=True, exist_ok=True)
        print(config)
        with open(config_file, "w") as f:
            json.dump(config, f)
        print(f"Log path written to {config_file}")
    else:
        print("Log file could not be found. Check your spelling and try again.")
        sys.exit(1)


def set_api_url(_):
    url = input("Enter the base URL for your API (e.g. http://api.example.com): ")
    if check_server_health(url):
        print("API URL verified")
        config_file = get_store_path() / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
            config["api_url"] = url
        else:
            config = {"api_url": url}
        with open(config_file, "w") as f:
            json.dump(config, f)
        print(f"API URL written to {config_file}")
    else:
        print(
            "Server is down or url is incorrect. Check your spelling or try again later."
        )

def set_novel_home(_):
    novel_home = input("Enter the name of the directory where you want to store your novel projects: ")
    print("Locating novel directory...")
    novel_home_path = find_file(novel_home)
    config_file = get_store_path() / "config.json"
    print("Loading current config...")
    if novel_home_path.exists():
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
            config["novel_home"] = str(novel_home_path)
        else:
            config = {"novel_home": str(novel_home_path)}
        print(config)
        with open(config_file, "w") as f:
            json.dump(config, f)
        print(f"Novel home path written to {config_file}")
    else:
        print(f"Novel home directory could not be found. Check your spelling and try again.")
        sys.exit(1)
def parse_config(subparsers):
    config_parser = subparsers.add_parser("config")
    config_subparsers = config_parser.add_subparsers(dest="subcommand")

    log_parser = config_subparsers.add_parser("log")
    log_parser.set_defaults(func=set_log_file)

    api_parser = config_subparsers.add_parser("api")
    api_parser.set_defaults(func=set_api_url)

    novel_home_parser = config_subparsers.add_parser("novel")
    novel_home_parser.set_defaults(func=set_novel_home)
