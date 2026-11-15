import json
import sys

from wlogs import load_config
from wlogs.commands.auth import send_auth_request


def get_all_records(endpoint: str) -> list[dict]:
    request = {"method": "GET", "endpoint": f"{load_config()['api_url']}/{endpoint}"}
    res = send_auth_request(request)
    if 400 <= res.status_code < 500:
        print_error_message(res)
        sys.exit(1)
    else:
        return res.json()


def print_error_message(res):
    print(f"An error occurred: {res.status_code} {res.reason}")
    try:
        print(f"Error message: {res.json()}")
    except json.JSONDecodeError:
        print("No error message returned.")


def get_record_id(code: str, endpoint: str, property_name: str = "code") -> int:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/{property_name}/{code}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print(f"Record {code} not found at {request['endpoint']}.")
        sys.exit(1)
    elif 400 <= res.status_code < 500:
        print_error_message(res)
        sys.exit(1)
    else:
        record = res.json()
        return record["id"]


def get_record_by_name(name: str, endpoint: str) -> list[dict | None]:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/name/{name}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    else:
        print_error_message(res)
        sys.exit(1)


def get_record_by_code(code: str, endpoint: str) -> dict[str, str | int | None]:
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
        print_error_message(res)
        sys.exit(1)


def get_record_by_id(id: int, endpoint: str) -> dict[str, str | int | None]:
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/{id}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print(f"Record not found at {request['endpoint']}.")
        sys.exit(1)
    elif 200 <= res.status_code < 300:
        return res.json()
    else:
        print_error_message(res)
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
        print_error_message(res)
        sys.exit(1)


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
        print_error_message(res)
        sys.exit(1)


def send_update_request(payload: list[dict], endpoint: str, record_id: int):
    request = {
        "method": "PATCH",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/{record_id}",
        "payload": payload,
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print(f"Record updated successfully at {request['endpoint']}")
    elif res.status_code == 404:
        print(f"Record not found at {request['endpoint']}.")
        sys.exit(1)
    else:
        print_error_message(res)
        sys.exit(1)
