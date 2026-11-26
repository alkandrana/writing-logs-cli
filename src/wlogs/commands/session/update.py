import sys
from datetime import datetime, timedelta
from typing import Required

from wlogs.utils.basic_utils import to_zulu

from ...utils.crud import (
    build_patch,
    get_record_by_code,
    get_record_id,
    send_update_request,
)


def get_start_time(code, prop_name):
    session = get_record_by_code(code, "sessions")
    date_obj = datetime.fromisoformat(str(session[prop_name])).astimezone()
    print(f"Old timestamp: {date_obj}")
    date_map = {
        "year": f"{date_obj.year:04d}",
        "month": f"{date_obj.month:02d}",
        "day": f"{date_obj.day:02d}",
        "hour": f"{date_obj.hour:02d}",
        "minute": f"{date_obj.minute:02d}",
        "second": f"{date_obj.second:02d}",
    }
    components = [
        "year",
        "month",
        "day",
        "hour",
        "second",
        "minute",
        "I want to change multiple components",
    ]
    print("Which component of the timestamp would you like to change? ")
    for i, part in enumerate(components):
        print(f"{i}. {part}")
    choice = input("Select the corresponding number: ")
    selection = components[int(choice)]

    if int(choice) == 6:
        year = input("Year (YYYY): ")
        month = input("Month (MM): ")
        day = input("Day (DD): ")
        hour = input("Hour (HH): ")
        minute = input("Minute (MM): ")
        second = input("Second (SS): ")
        date_str = f"{year}-{month}-{day}T{hour}:{minute}:{second}"
    else:
        date_map[selection] = input(f"Value you want to change the {selection} to: ")
        date_str = f"{date_map['year']}-{date_map['month']}-{date_map['day']}T{date_map['hour']}:{date_map['minute']}:{date_map['second']}"
    print(f"Local update string: {date_str}")
    updated_obj = datetime.fromisoformat(date_str).astimezone()
    print(f"UTC update string: {to_zulu(updated_obj.isoformat())}")
    return to_zulu(updated_obj.isoformat())


def adjust_date(period, code):
    timespan = timedelta(days=period)
    session = get_record_by_code(code, "sessions")
    try:
        current_date = datetime.fromisoformat(str(session["date"])).date()
    except ValueError:
        print("Date string is not a valid ISO format (e.g., YYYY-MM-DD)")
        sys.exit(1)
    new_date = current_date + timespan
    return new_date


def update_session(args):
    payload = []
    session_id = get_record_id(args.code, "sessions")
    if len(sys.argv) <= 2:
        print("No valid property submitted for update.")
        sys.exit(1)

    if not session_id:
        print(f"No record found for session {args.code}")
        sys.exit(1)

    if args.date:
        new_date = adjust_date(args.date, args.code)
        payload.append(build_patch("date", new_date.isoformat()))

    if args.type:
        payload.append(build_patch("type", args.type))

    if args.note:
        payload.append(build_patch("comments", args.note))
    if args.start:
        new_start = get_start_time(args.code, "startTime")
        payload.append(build_patch("startTime", new_start))
    if args.stop:
        new_stop = get_start_time(args.code, "stopTime")
        payload.append(build_patch("stopTime", new_stop))

    print(f"Ready to update: {payload}")
    c = input("Proceed? (y/n): ")
    if c.lower() == "y":
        send_update_request(payload, "sessions", session_id)


def parse_update_session(session_subparsers):
    update_parser = session_subparsers.add_parser("update")
    update_parser.add_argument(
        "--code",
        "-c",
        required=True,
        help="Unique identifier for the session you want to change.",
    )
    update_parser.add_argument(
        "--date",
        "-d",
        required=False,
        type=int,
        help="Number of days to change date value to.\nTo move the date backward, use a negative number.",
    )
    update_parser.add_argument(
        "--start",
        "-b",
        required=False,
        action="store_true",
        help="Initiates an interactive script for changing start time to a new value using a valid ISO string.",
    )
    update_parser.add_argument(
        "--stop",
        "-e",
        required=False,
        action="store_true",
        help="Initiates an interactive script for changing stop time to a new value using a valid ISO string.",
    )
    update_parser.add_argument(
        "--type", "-t", required=False, help="Update value for session type."
    )
    update_parser.add_argument(
        "--note", "-n", required=False, help="Add or change session comment."
    )
    update_parser.set_defaults(func=update_session)
