from wlogs import load_config
from ...utils.crud import get_record_id, build_patch, send_update_request

def update_session(args):
    payload = []
    session_id = get_record_id(args.code, "sessions")
    if len(sys.argv) <= 2:
        print("No valid property submitted for update.")
        sys.exit(1)

    if not session_id:
        print(f"No record found for session {args.code}")
        sys.exit(1)
    
    if args.type:
        payload.append(build_patch("type", args.type))

    if args.note:
        payload.append(build_patch("comments", args.note))

    request = {
        "endpoint": f"{load_config()['api_url']}/sessions/{session_id}",
        "method": "PATCH",
        "payload": payload
    }
    print(f"Ready to update: {payload}")
    c = input("Proceed? (y/n): ")
    if c.lower() == 'y':
        send_update_request(request)

def parse_update_session(session_subparsers):
    update_parser = session_subparsers.add_parser("update")
    update_parser.add_argument("--code", "-c", required=True, help="Unique identifier for the session you want to change.")
    update_parser.add_argument("--type", "-t", required=False, help="Update value for session type.")
    update_parser.add_argument("--note", "-n", required=False, help="Add or change session comment.")
    update_parser.set_defaults(func=update_session)
