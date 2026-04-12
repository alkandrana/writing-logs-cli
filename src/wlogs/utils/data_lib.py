from datetime import datetime
import sys
from typing import Any
from pathlib import Path

### DATES ###
def now_iso() -> str:
    # ISO-8601 with local offset, seconds precision
    return datetime.now().astimezone().isoformat(timespec="seconds")

def convert_to_session(file_data: dict[str, Any], words: int):
    session = {
        "date": file_data["date"],
        "startTime": file_data["start_time"],
        "stopTime": now_iso(), 
        "words": words,
        "sceneCode": file_data["scene_code"]
    }
    return session

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

### OTHER ###

# Number validation
def prompt_int(label: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.", file=sys.stderr)

# Word Count validation
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

def validate_session(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        print("No session in progress.", file=sys.stderr)
        sys.exit(2)
    data["stop_time"] = now_iso()
    if not data["scene_code"] or not data["start_time"]:
        print("State file is missing sceneCode/startTime. Try `wlogs cancel` and start again.", file=sys.stderr)
        sys.exit(2)
    return data

def get_novel_parent():
    novels = [f for f in Path(Path.home()).rglob("novels")]
    parents = [f for f in novels[0].parents]
    novel_parent = parents[1]
    for n in novels:
        parents = [f for f in n.parents]
        if novel_parent != parents[1]:
            print("Novel path is not universal")
            sys.exit(0)
    return novel_parent