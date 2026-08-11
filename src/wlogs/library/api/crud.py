from .auth import send_auth_request
from ... import load_config
import sys
from typing import Any


def get_record_id(code, endpoint):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()["api_url"]}/{endpoint}/code/{code}",
    }
    res = send_auth_request(request)
    if res.status_code == 404:
        print(f"Record {code} not found at {request["endpoint"]}.")
        sys.exit(1)
    else:
        return res.json()

def get_record_by_code(code, endpoint):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/{endpoint}/code/{code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300 or res.status_code == 404:
        return res
    else:
        print("An error occurred: ", res.status_code, res.reason, res.json())
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

def get_patch_payload(value, prop):
    payload = [
        {
            "op": "replace",
            "path": prop,
            "value": value
        }]
    return payload

def post_record(data, endpoint):
    request = {
        "method": "POST",
        "endpoint": f"{load_config()["api_url"]}/{endpoint}",
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