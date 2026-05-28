# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
import sys

import requests
from typing import Any


class Api:
    def __init__(self, url) -> None:
        self.api_url = url

    def record_exists(self, endpoint, code) -> bool:
        r = requests.get(f"{self.api_url}/{endpoint}/{code}", timeout=5)
        if r.status_code == 200 and len(r.json()) > 0:
            return True
        else:
            return False

    def send_post_request(self, payload, endpoint) -> dict:
        # POST /sessions with JSON body. Returns parsed JSON response.
        # Raises requests exceptions on errors.
        url = f"{self.api_url}/{endpoint}"
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()

    def send_patch_request(self, payload, endpoint) -> dict:
        url = f"{self.api_url}/{endpoint}"
        res = requests.patch(url, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()

    def handle_post_errors(self, e):
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

    def post_results(self, payload: dict[str, Any], endpoint) -> dict[str, Any]:
        created = {}
        try:
            created = self.send_post_request(payload, endpoint)
        except requests.HTTPError as e:
            self.handle_post_errors(e)
        except requests.RequestException as e:
            print("Network error:", e, file=sys.stderr)
            sys.exit(1)
        return created

    def patch_results(self, payload: dict[str, Any], endpoint) -> dict[str, Any]:
        updated = {}
        try:
            updated = self.send_patch_request(payload, endpoint)
        except requests.HTTPError as e:
            self.handle_post_errors(e)
        except requests.RequestException as e:
            print("Network error:", e, file=sys.stderr)
            sys.exit(1)
        return updated
