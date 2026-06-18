from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Protocol

from utils.http_client import HttpClient


class SqlExecutor(Protocol):
    def execute(self, sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> int:
        ...


@dataclass
class RecoveryAction:
    name: str
    action: Callable[[], None]


class DataRecovery:
    """Register cleanup actions during a test and run them after the test."""

    def __init__(
        self,
        api_client: HttpClient | None = None,
        db_client: SqlExecutor | None = None,
        logger: Any | None = None,
    ) -> None:
        self.api_client = api_client
        self.db_client = db_client
        self.logger = logger
        self._actions: list[RecoveryAction] = []

    def add_cleanup(self, name: str, action: Callable[[], None]) -> None:
        self._actions.append(RecoveryAction(name=name, action=action))

    def delete_created(self, path: str, payload: dict[str, Any], name: str | None = None) -> None:
        action_name = name or f"delete created data by {path}"

        def cleanup() -> None:
            if self.api_client is None:
                raise RuntimeError("api_client is required for API data recovery")
            response = self.api_client.post(path, json=payload)
            if response.status_code >= 400:
                raise AssertionError(f"{action_name} failed: {response.status_code}, {response.text}")

        self.add_cleanup(action_name, cleanup)

    def restore_updated(self, path: str, payload: dict[str, Any], name: str | None = None) -> None:
        action_name = name or f"restore updated data by {path}"

        def cleanup() -> None:
            if self.api_client is None:
                raise RuntimeError("api_client is required for API data recovery")
            response = self.api_client.post(path, json=payload)
            if response.status_code >= 400:
                raise AssertionError(f"{action_name} failed: {response.status_code}, {response.text}")

        self.add_cleanup(action_name, cleanup)

    def execute_sql(
        self,
        sql: str,
        params: Iterable[Any] | dict[str, Any] | None = None,
        name: str | None = None,
    ) -> None:
        action_name = name or f"execute recovery sql: {sql}"

        def cleanup() -> None:
            if self.db_client is None:
                raise RuntimeError("db_client is required for database data recovery")
            self.db_client.execute(sql, params)

        self.add_cleanup(action_name, cleanup)

    def delete_created_by_sql(
        self,
        sql: str,
        params: Iterable[Any] | dict[str, Any] | None = None,
        name: str | None = None,
    ) -> None:
        action_name = name or "delete created data by sql"
        self.execute_sql(sql=sql, params=params, name=action_name)

    def restore_updated_by_sql(
        self,
        sql: str,
        params: Iterable[Any] | dict[str, Any] | None = None,
        name: str | None = None,
    ) -> None:
        action_name = name or "restore updated data by sql"
        self.execute_sql(sql=sql, params=params, name=action_name)

    def run(self) -> None:
        errors: list[str] = []

        while self._actions:
            recovery_action = self._actions.pop()
            try:
                recovery_action.action()
                if self.logger:
                    self.logger.info("data recovery success: %s", recovery_action.name)
            except Exception as exc:
                message = f"data recovery failed: {recovery_action.name}, error: {exc}"
                errors.append(message)
                if self.logger:
                    self.logger.error(message)

        if errors:
            raise AssertionError("\n".join(errors))
