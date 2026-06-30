"""Local hackathon login system backed by users.json."""

import json
from pathlib import Path

from helpers.paths import USERS_FILE


def _load_users() -> dict[str, str]:
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict[str, str]) -> None:
    with USERS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."

    users = _load_users()
    if username in users:
        return False, "Username already exists."

    users[username] = password
    _save_users(users)
    return True, "Registration successful. You can now log in."


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Authenticate a user. Returns (success, message)."""
    username = username.strip()
    if not username or not password:
        return False, "Invalid username/password."

    users = _load_users()
    if username not in users or users[username] != password:
        return False, "Invalid username/password."

    return True, "Login successful."
