from wlogs import load_config
from wlogs.commands.auth import send_auth_request


def post_session(body):
    request = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/sessions",
        "payload": body,
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print(f"Session saved to {request['endpoint']}")
    else:
        print(f"Unable to save session: {res.status_code, res.reason, res.json()}")
    return res
