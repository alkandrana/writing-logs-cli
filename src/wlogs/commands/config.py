import sys
from typing import Any
from wlogs.utils.file_lib import find_files
import os
from pathlib import Path
def get_config_path():
    xdg_state = os.getenv("XDG_STATE_HOME")
    if xdg_state:
        root = Path(xdg_state)
    else:
        root = Path.home() / ".local" / "state"
    path = root / "wlogs"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def load_config() -> dict[str, Any]:
    config_path = get_config_path() / ".config"
    if not config_path.exists():
        print("Config has not been set up. Run it with 'sudo wlogs config'")
        sys.exit(1)
    config = {}
    with open(config_path, "r") as f:
        config_lines = f.readlines()
        novels_path = Path(config_lines[0].strip())
        log_path = Path(config_lines[1].strip())
        if not novels_path.exists() or not log_path.exists():
            choice = input("One or more of your config paths are no longer valid. Run setup now? (y/n): ")
            if choice.lower() == "y":
                get_config()
            else:
                sys.exit(1)
        config['novels_path'] = novels_path
        config['log_path'] = log_path
        config['api_url'] = config_lines[2].strip()
        config['state'] = get_config_path()
    return config

def get_config(args = None) -> None:
    print("Starting config: ")
    # novel directory
    novels_dir = input("Enter the name of the directory where your novel projects are stored: ")
    print(f"Retrieving {novels_dir} path. This may take a few minutes...")
    novels_path = find_files(novels_dir, full_name=True)
    print(f"Novel projects are located at {novels_path}")
    # API url
    api_url = input("Enter the domain of the api you want to save sessions to (e.g.: https://api.example.com): ")
    # name of log file
    log_file = input("Enter the name of the local file where you would like to save sessions: ")
    print("Searching for log file in novels directory...")
    log_path = find_files(log_file, search_dir=novels_path, full_name=True)
    print(f"Log file is located at {log_path}")
    config_path = get_config_path() / ".config"
    print("Saving config details...")
    with open(config_path, "w") as f:
        f.write(f"{novels_path}\n{log_path}\n{api_url}")
        print("Config saved successfully")

def parse_config(subparsers):
    config_parser = subparsers.add_parser("config", help="Configure basic filesystem operations. Searching the filesystem may require administrative permissions, so it is recommended to run with sudo: 'sudo wlogs config'")
    config_parser.add_argument("--root", required=False, help="Directory where your novel projects are stored")
    config_parser.add_argument("--log", required=False, help="Local file to save sessions to")
    config_parser.add_argument("--api", required=False, help="Domain of the api you want to save sessions to (e.g.: https://api.example.com)")
    config_parser.set_defaults(func=get_config)