import sys

from wlogs import load_config
from wlogs.library.api.auth import send_auth_request


def get_status_id(name: str) -> str:
    if name not in ["pending", "writing", "finished", "aborted"]:
        print("Invalid status name.")
        sys.exit(1)
    else:
        request = {
            "method": "GET",
            "endpoint": f"{load_config()['api_url']}/status/{name}",
        }
        res = send_auth_request(request)
        if 200 <= res.status_code < 300:
            options: list[dict[str, str]] = res.json()
            if len(options) == 1:
                return options[0]["id"]
            elif len(options) > 1:
                print("Multiple options found. Make a selection: ")
                for i, option in enumerate(options):
                    print(f"{i}. {option}")
                choice = input("Select an option: ")
                return options[int(choice)]["id"]
            else:
                print("No options found.")
                sys.exit(1)
        else:
            print(f"An error occurred: {res.status_code} {res.json()}")
            sys.exit(1)
            
def get_status_name(status_id: int) -> str:
    request = {
            "method": "GET",
            "endpoint": f"{load_config()['api_url']}/status/{status_id}"
            }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        status = res.json()
        return status['name']
    elif res.status_code == 404:
        print("No status found for that id.")
        sys.exit(1)
    else:
        print(f"An error occurred: {res.status_code} {res.json()}")
        sys.exit(1)

