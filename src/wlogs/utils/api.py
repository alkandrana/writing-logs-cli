# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
import csv
import sys

import requests
from requests import HTTPError
from typing import Any

BASE_URL = "http://localhost:8081/api"

def scene_exists(code: str) -> bool:
    r = requests.get(f"{BASE_URL}/scenes/{code}", timeout=5)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()

def send_post_request(payload: dict,  endpoint: str) -> dict:
    # POST /sessions with JSON body. Returns parsed JSON response.
    # Raises requests exceptions on errors.
    url = f"{BASE_URL}/{endpoint}"
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

def send_patch_request(payload: dict, endpoint: str) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    res = requests.patch(url, json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

def handle_post_errors(e):
    r = e.response
    if r is None:
        print("API error.", file=sys.stderr)
    else:
        try:
            msg = r.json().get("message") or r.text
        except ValueError:
            msg = r.text
        print(f"API error: ({r.status_code}): {msg}", file=sys.stderr)
        sys.exit(1)

def post_results(payload: dict[str, Any], endpoint) -> dict[str, Any]:
    try:
        created = send_post_request(payload, endpoint)
    except requests.HTTPError as e:
        handle_post_errors(e)
    except requests.RequestException as e:
        print("Network error:", e, file=sys.stderr)
        sys.exit(1)
    return created

def patch_results(payload: dict[str, Any], endpoint) -> dict[str, Any]:
    try:
        updated = send_patch_request(payload, endpoint)
    except requests.HTTPError as e:
        handle_post_errors(e)
    except requests.RequestException as e:
        print("Network error:", e, file=sys.stderr)
        sys.exit(1)
    return updated
