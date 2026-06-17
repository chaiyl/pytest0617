from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class MockResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class MockLoginApiClient:
    def __init__(self, users: dict[str, dict[str, Any]]) -> None:
        self.users = users

    def post(self, path: str, json: dict[str, Any] | None = None, **kwargs: Any) -> MockResponse:
        if path != "/login":
            return self._error(404, "NOT_FOUND", "api path is not found")
        return self.login(json)

    def login(self, payload: dict[str, Any] | None) -> MockResponse:
        if payload is None:
            return self._error(400, "INVALID_REQUEST", "request body is required")

        username = payload.get("username")
        password = payload.get("password")

        if username in (None, ""):
            return self._error(400, "USERNAME_REQUIRED", "username is required")

        if password in (None, ""):
            return self._error(400, "PASSWORD_REQUIRED", "password is required")

        if not isinstance(username, str) or not isinstance(password, str):
            return self._error(400, "INVALID_FIELD_TYPE", "username and password must be strings")

        user = self.users.get(username)
        if user is None:
            return self._error(401, "INVALID_CREDENTIALS", "username or password is incorrect")

        if user.get("locked", False):
            return self._error(423, "ACCOUNT_LOCKED", "account is locked")

        if password != user["password"]:
            return self._error(401, "INVALID_CREDENTIALS", "username or password is incorrect")

        return MockResponse(
            status_code=200,
            body={
                "code": "OK",
                "message": "login success",
                "data": {
                    "token": f"demo-token-{uuid4().hex}",
                    "user_id": user["id"],
                    "username": username,
                },
            },
        )

    @staticmethod
    def _error(status_code: int, code: str, message: str) -> MockResponse:
        return MockResponse(
            status_code=status_code,
            body={
                "code": code,
                "message": message,
                "data": None,
            },
        )
