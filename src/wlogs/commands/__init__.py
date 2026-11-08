import sys

import requests


def send_request(request):
    if request["method"] == "POST":
        res = requests.post(request["endpoint"], json=request["payload"])
    elif request["method"] == "GET":
        res = requests.get(request["endpoint"])
    else:
        print("Request method not supported.")
        sys.exit(1)
    return res


def validate_response(res):
    if 200 <= res.status_code < 300:
        print("Request successful.")
    elif 400 <= res.status_code < 500:
        print(f"Error: {res.status_code} - {res.reason}")
        print(f"Error message: {res.json()}")
    else:
        print("Something went wrong. Please try again later.")
