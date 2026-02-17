# Created by Rosa Lee Myers 02-12-2026 with help from ChatGPT
import argparse
from datetime import datetime
from pathlib import Path
import json
from typing import Any
import sys
import requests
# from .api import *
from .config import state_path

def now_iso() -> str:
    # ISO-8601 with local offset, seconds precision
    return datetime.now().astimezone().isoformat(timespec="seconds")

def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def save_state(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def clear_state(path: Path) -> None:
    if path.exists():
        path.unlink()

def prompt_int(label: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.", file=sys.stderr)

def format_elapsed(start_iso: str) -> str:
    try:
        start = datetime.fromisoformat(start_iso)
        elapsed = datetime.now().astimezone() - start.astimezone()
        total_seconds = int(elapsed.total_seconds())
        if total_seconds < 0:
            return "(-)"
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except Exception:
        return "(unknown)"

def validate_words(start_words: int, stop_words: int, words: int) -> int:
    if words is None and stop_words is None:
        if start_words is not None:
            print(f"Start words: {start_words}")
            stop_words = prompt_int("Stop words (to compute delta): ")
        else:
            words = prompt_int("Words written: ")

    # If user provided stop_words, compute delta (requires start_words)
    if stop_words is not None:
        if start_words is None:
            print("You provided --stop-words but no startWords were recorded.", file=sys.stderr)
            print("Either start with `wlogs start --start-words <N>` or stop with `--words <N>`.", file=sys.stderr)
            sys.exit(2)
        words = stop_words - int(start_words)
        if words < 0:
            print(f"Computed words is negative ({words}). Check start/stop word counts.", file=sys.stderr)
            sys.exit(2)

    if words is None:
        print("Words could not be determined.", file=sys.stderr)
        sys.exit(2)
    return words

def scene_exists(code: str) -> bool:
    r = requests.get(f"{BASE_URL}/scenes/{code}", timeout=5)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    r.raise_for_status()

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

def session_results(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        created = post_session(payload)
    except requests.HTTPError as e:
        handle_post_errors(e)
    except requests.RequestException as e:
        print("Network error:", e, file=sys.stderr)
        sys.exit(1)
    return created

def scene_results(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        created = post_scene(payload)
    except requests.HTTPError as e:
        handle_post_errors(e)
    except requests.RequestException as e:
        print("Network error:", e, file=sys.stderr)
        sys.exit(1)
    return created
def clean_data(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        print("No session in progress. Use `wlogs start --scene <CODE>` first.", file=sys.stderr)
        sys.exit(2)
    data["stopTime"] = now_iso()
    if not data["sceneCode"] or not data["startTime"]:
        print("State file is missing sceneCode/startTime. Try `wlogs cancel` and start again.", file=sys.stderr)
        sys.exit(2)
    return data
def cmd_start(args: argparse.Namespace) -> None:
    path = state_path()
    current = load_state(path)
    if current:
        print("A session is already in progress:", file=sys.stderr)
        print(f"    sceneCode:  {current.get('sceneCode')}", file=sys.stderr)
        print(f"    startTime:  {current.get('startTime')} (elapsed {format_elapsed(current.get('startTime',''))})", file=sys.stderr)
        print("User `wlogs cancel` to discart it, or `wlogs stop` to submit it.", file=sys.stderr)
        sys.exit(2)
    data: dict[str, Any] = {
        "sceneCode": args.scene,
        "startTime": now_iso(),
    }
    if args.start_words is not None:
        data["startWords"] = args.start_words

    save_state(path, data)
    msg = f"Started: {data['sceneCode']} @ {data['startTime']}"
    if "startWords" in data:
        msg += f" (startWords {data['startWords']})"
    print(msg)

def cmd_status(_: argparse.Namespace) -> None:
    path = state_path()
    data = load_state(path)
    if not data:
        print("No session in progress.")
        return

    start_time = data.get("startTime", "?")
    scene = data.get("sceneCode", "?")
    start_words = data.get("startWords", None)

    print(f"Session in progress:")
    print(f"    sceneCode:  {scene}")
    print(f"    startTime:  {start_time} (elapsed {format_elapsed(start_time)})")
    if start_words is not None:
        print(f"    startWords: {start_words}")

def cmd_cancel(_: argparse.Namespace) -> None:
    path = state_path()
    if not path.exists():
        print("No session to cancel.")
        return
    data = load_state(path)
    clear_state(path)
    print(f"Canceled session: {data.get('sceneCode', '?')} @ {data.get('startTime', '?')}")

def cmd_stop(args: argparse.Namespace) -> None:
    path = state_path()
    # Gather session data into variables
    data = clean_data(load_state(path))
    # Determine words:
    words: int | None = args.words
    stop_words: int | None = args.stop_words
    start_words: int | None = data.get("startWords", None)
    words = validate_words(start_words, stop_words, words)
    ### JSON DATA ###
    payload = {
        "sceneCode": data["sceneCode"],
        "startTime": data["startTime"],
        "stopTime": data["stopTime"],
        "words": int(words),
    }
    ### POST ###
    if not scene_exists(payload["sceneCode"]):
        print(f"Scene {payload['sceneCode']} does not exist.")
        add_scene = input("Would you like to create it? (y/n) ")
        if add_scene == "y":
            name = input("Scene Name: ")
            scene_data = {
                "code": payload["sceneCode"],
                "sceneName": name,
            }
            scene_results(scene_data)
        else:
            sys.exit(0)

    created = session_results(payload)
    # Only clear state if the POST succeeded
    clear_state(path)
    # Friendly output
    print(f"Submitted: {data["scene"]} | {payload['words']} words | {data["start_time"]}")
    print(created)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='wlogs')
    subparsers = parser.add_subparsers(dest='command', required=True)

    start_parser = subparsers.add_parser("start", help="Start a writing session (stores local state)")
    start_parser.add_argument("--scene", required=True, help="Scene code (e.g., AKT_JRM)")
    start_parser.add_argument("--start-words", type=int, default=None, help="Starting word count (optional)")
    start_parser.set_defaults(func=cmd_start)

    stop_parser = subparsers.add_parser("stop", help="Stop the current session and POST it to the API")
    stop_parser.add_argument("--stop-words", type=int, default=None, help="Stopping words count (delta computed if startWords exists)")
    stop_parser.add_argument("--words", type=int, default=None, help="Words written (direct)")
    stop_parser.set_defaults(func=cmd_stop)

    status_parser = subparsers.add_parser("status", help="Show the currently running session")
    status_parser.set_defaults(func=cmd_status)

    cancel_parser = subparsers.add_parser("cancel", help="Discard the currently running session")
    cancel_parser.set_defaults(func=cmd_cancel)
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)