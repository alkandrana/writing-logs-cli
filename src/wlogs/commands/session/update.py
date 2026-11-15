import sys
from datetime import datetime, timedelta

from ...utils.crud import (
    build_patch,
    get_record_by_code,
    get_record_id,
    send_update_request,
)


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
        "--type", "-t", required=False, help="Update value for session type."
    )
    update_parser.add_argument(
        "--note", "-n", required=False, help="Add or change session comment."
    )
    update_parser.set_defaults(func=update_session)
