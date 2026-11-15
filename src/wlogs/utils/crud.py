import json
import sys
from typing import Any

from wlogs import load_config
from wlogs.commands.auth import send_auth_request


def send_fetch_request(request: dict[str, Any]) -> dict[str, Any] | None:
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        print(f"An error occurred: {res.status_code}, {res.reason}")
        return


def print_error_message(res):
    print(f"An error occurred: {res.status_code} {res.reason}")
    try:
        print(f"Error message: {res.json()}")
    except json.JSONDecodeError:
        print("No error message returned.")
    sys.exit(1)


def get_record_id(code: str, endpoint: str) -> int | None:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/code/{code}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print(f"Record {code} not found at {request['endpoint']}.")
        return
    elif 400 <= res.status_code < 500:
        print_error_message(res)
    else:
        record = res.json()
        return record["id"]


def get_record_by_code(code, endpoint):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/code/{code}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print(f"{endpoint} not found at {request['endpoint']}")
        sys.exit(0)
    elif 200 <= res.status_code < 300:
        return res.json()
    else:
        print("An error occurred: ", res.status_code, res.reason)
        try:
            print(f"Error Message: {res.json()}")
        except json.JSONDecodeError:
            print("No error message returned.")
        sys.exit(1)


def get_record_by_id(id, endpoint):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/{id}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print("Record not found.")
        sys.exit(1)
    elif 200 <= res.status_code < 300:
        return res.json()
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())
        sys.exit(1)


def check_record_exists(code: str, endpoint: str):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/code/{code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return True
    elif res.status_code == 404:
        return False
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())


def get_status_values() -> list[dict[str, Any]]:
    status_req = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/status",
    }
    res = send_auth_request(status_req)
    if not 200 <= res.status_code < 300:
        print(f"Error: {res.status_code} - {res.reason}")
        sys.exit(1)
    else:
        return res.json()


def build_patch(property_name: str, value: str | int) -> dict[str, str | int]:
    data = {"op": "replace", "path": f"/{property_name}", "value": value}
    print(f"Patch built: {data}")
    return data


def post_record(data: dict[str, str | int], endpoint: str):
    request = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/{endpoint}",
        "payload": data,
    }
    res = send_auth_request(request)
    if res.status_code == 409:
        print("Record already added. Skipping...")
    elif 200 <= res.status_code < 300:
        print(f"Record successfully added:\n{data}\nProceeding...")
    else:
        error = res.json()
        print("An error occured: ", res.status_code, res.reason)
        print(error)
        sys.exit(1)


def send_update_request(request: dict, record: str):
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print(f"{record.capitalize()} updated successfully")
    elif res.status_code == 404:
        print(f"{record.capitalize()} not found.")
        sys.exit(1)
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())
        sys.exit(1)
