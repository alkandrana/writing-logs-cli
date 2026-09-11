import os
import sys
from pathlib import Path
from collections.abc import Generator
from wlogs import load_config


def fast_search(
        target_filename: str, target_dir: Path | str | None = None, full_name: bool = False
        ) -> Generator[Path]:
    # os.scandir returns an iterator that points directly to system memory
    for entry in os.scandir(target_dir):
        if not entry.name.startswith(".") and not entry.name in ["Library", "Downloads"]:
            condition = (
                target_filename.lower() == entry.name.lower()
                if full_name
                else target_filename.lower() in entry.name.lower()
            )
            if condition:
                yield Path(entry.path)
            if entry.is_dir(follow_symlinks=False):
                # Recurse into subdirectories
                try:
                    yield from fast_search(
                        target_filename, target_dir=entry.path, full_name=full_name
                    )
                except PermissionError:
                    continue


def find_file(
        target_filename: str, target_dir: Path | str | None = None, full_name: bool = False
):
    if not target_dir:
        target_dir = Path.home()
    options = [p for p in fast_search(target_filename, target_dir, full_name)]
    if len(options) == 1:
        choice = options[0]
    elif len(options) > 1:
        print(f"Multiple options found: {options}. Make a selection:")
        for i, option in enumerate(options):
            print(f"\t{i + 1}. {option}")
        choice = input("\tSelect an option: ")
        choice = options[int(choice) - 1]
    else:
        print(f"No files match your search criteria: {target_filename}")
        return None
        # sys.exit(1)
    return Path(choice)

def get_book_path(book_id: str):
    path = find_file(book_id, target_dir=load_config()["novel_home"], full_name=True)
    if path is None or not path.exists():
        print("File path not found. Verify that the book id corresponds to all or part of a directory name and try again.")
        sys.exit(1)
    else:
        return path
