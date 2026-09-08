import sys, requests, csv, os
from ..crud import post_record





def get_records_from_api(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            print("Successfully retrieved records to post")
            return res.json()
        else:
            print("Request failed: ", res.status_code, res.reason)
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("The server appears to be down.")
        sys.exit(1)


def transfer(base, endpoint, format_records):
    records = get_records_from_api(f"{base}/{endpoint}")
    formatted = format_records(records)
    for rec in formatted:
        post_record(rec, endpoint)


def batch_from_file(path, endpoint, format_records):
    records = get_records_from_file(path)
    formatted = format_records(records)
    for rec in formatted:
        post_record(rec, endpoint)




