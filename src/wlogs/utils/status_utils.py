import sys

from wlogs import load_config
from wlogs.commands.auth import send_auth_request
from wlogs.utils.crud import print_error_message


def get_status_name(status_id: int) -> str:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/status/{status_id}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        status = res.json()
        return status["name"]
    elif res.status_code == 404:
        print(f"No status found for {status_id}.")
        sys.exit(1)
    else:
        print_error_message(res)
        sys.exit(1)
