from __future__ import annotations

import secrets

from app.core.rbac import DEMO_USERS


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, str]] = {}

    def login(self, username: str, password: str) -> dict[str, str] | None:
        user = DEMO_USERS.get(username)
        if not user or user["password"] != password:
            return None

        token = secrets.token_urlsafe(32)
        session = {"token": token, "username": username, "role": user["role"]}
        self._sessions[token] = session
        return session

    def get(self, token: str) -> dict[str, str] | None:
        return self._sessions.get(token)
