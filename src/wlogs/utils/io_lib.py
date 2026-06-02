from typing import Any


def create_if_not_exists(self, payload: dict[str, Any], endpoint: str) -> dict:
    choice = input("That record does not exist. Create it? (y/n) ")
    if choice == "y":
        self.send_post_request(payload, endpoint)
