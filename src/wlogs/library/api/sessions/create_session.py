from wlogs import load_config
from wlogs.library.api.auth import send_auth_request
from ..scenes.scene import get_one_scene
from wlogs.library.dates import to_zulu, format_dates

#   REDUNDANT
# def get_scene_id(code):
#     print(f"Fetching scene with code {code}...")
#     res = get_one_scene(code)
#     if res.status_code == 404:
#         print("No scene with that code.")
#         sys.exit(1)
#     else:
#         scene = res.json()
#     return scene["id"]


def build_session_body(args):
    format_dates({"date": args.date, "start": args.start, "stop": args.stop})
    body = {"date": args.date, "words": args.words}
    scene_id = get_scene_id(args.code)
    body["sceneId"] = scene_id
    if args.start:
        body["startTime"] = to_zulu(args.start)
    if args.stop:
        body["stopTime"] = to_zulu(args.stop)
    if args.note:
        body["comments"] = args.note
    return body


def post_session(body):
    request = {
        "method": "POST",
        "endpoint": f"{load_config()['api_url']}/sessions",
        "payload": body,
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        print(f"Session saved to {request['endpoint']}")
    else:
        print(f"Unable to save session: {res.status_code, res.reason, res.json()}")
    return res


def create_session(args):
    body = build_session_body(args)
    post_session(body)


def parse_create_session(session_subparsers):
    create_parser = session_subparsers.add_parser("create")
    create_parser.add_argument("--date", "-d", required=True)
    create_parser.add_argument("--words", "-w", required=True)
    create_parser.add_argument(
        "--code",
        "-c",
        required=True,
        help="Code of the scene to associate with the session.",
    )
    create_parser.add_argument("--start", "-b", required=False)
    create_parser.add_argument("--stop", "-e", required=False)
    create_parser.add_argument("--note", "-n", required=False)
    create_parser.set_defaults(func=create_session)

