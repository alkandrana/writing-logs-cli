from datetime import datetime
import sys
from typing import Any


### DATES ###
def get_current_timestamp() -> str:
    # ISO-8601 with local offset, seconds precision
    return datetime.now().astimezone().isoformat(timespec="seconds")


def print_dict(data: dict[str, Any]):
    for key, value in data.items():
        print(f"{key}: {value}")


def print_options(options):
    output = 0
    for i, option in enumerate(options):
        print(f"{i}. {option}")
        choice = input("Select number: ")
        output = options[int(choice)]
    return output


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
        return f"{minutes}m {seconds}s"
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
def validate_words(start_words, stop_words, words) -> int:
    if words is None and stop_words is None:
        if start_words is not None:
            print(f"Start words: {start_words}")
            stop_words = prompt_int("Stop words (to compute delta): ")
        else:
            words = prompt_int("Words written: ")

    # If user provided stop_words, compute delta (requires start_words)
    if stop_words is not None:
        if start_words is None:
            print(
                "You provided --stop-words but no startWords were recorded.",
                file=sys.stderr,
            )
            print(
                "Either start with `wlogs start --start-words <N>` or stop with `--words <N>`.",
                file=sys.stderr,
            )
            sys.exit(2)
        words = stop_words - int(start_words)
        if words < 0:
            print(
                f"Computed words is negative ({words}). Check start/stop word counts.",
                file=sys.stderr,
            )
            sys.exit(2)

    if words is None:
        print("Words could not be determined.", file=sys.stderr)
        sys.exit(2)
    return words
