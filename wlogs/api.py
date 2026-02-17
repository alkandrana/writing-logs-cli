# Created by Rosa Lee Myers 2026-02-14 with help from ChatGPT
import csv
import sys

import requests
from requests import HTTPError
from typing import Any

BASE_URL = "http://localhost:8081"

def scene_exists(code: str) -> bool:
    r = requests.get(f"{BASE_URL}/scenes/{code}", timeout=5)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()
def post_session(payload: dict) -> dict:
    # POST /sessions with JSON body. Returns parsed JSON response.
    # Raises requests exceptions on errors.
    url = f"{BASE_URL}/sessions"
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

def post_scene(payload: dict) -> dict:
    url = f"{BASE_URL}/scenes"
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    return res.json()

