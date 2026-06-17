from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class MySqlClient:
    """Common MySQL helper for pytest setup, assertions, and cleanup."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.connection: Any | None = None

    def connect(self) -> None:
        if self.connection is not None and self.connection.open:
            return

        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pymysql is required for MySQL access. Run: python -m pip install -r requirements.txt"
            ) from exc

        self.connection = pymysql.connect(
            host=self.config["host"],
            port=int(self.config.get("port", 3306)),
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config.get("charset", "utf8mb4"),
            connect_timeout=int(self.config.get("connect_timeout", 10)),
            read_timeout=int(self.config.get("read_timeout", 10)),
            write_timeout=int(self.config.get("write_timeout", 10)),
            autocommit=False,
            cursorclass=DictCursor,
        )

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute(self, sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> int:
        connection = self._get_connection()
        with connection.cursor() as cursor:
            affected_rows = cursor.execute(sql, params)
        connection.commit()
        return affected_rows

    def execute_many(self, sql: str, params_list: Iterable[Iterable[Any] | dict[str, Any]]) -> int:
        connection = self._get_connection()
        with connection.cursor() as cursor:
            affected_rows = cursor.executemany(sql, params_list)
        connection.commit()
        return affected_rows

    def fetch_one(self, sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> dict[str, Any] | None:
        connection = self._get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> list[dict[str, Any]]:
        connection = self._get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return list(cursor.fetchall())

    def rollback(self) -> None:
        self._get_connection().rollback()

    def commit(self) -> None:
        self._get_connection().commit()

    def _get_connection(self) -> Any:
        if self.connection is None or not self.connection.open:
            self.connect()
        if self.connection is None:
            raise RuntimeError("mysql connection is not initialized")
        return self.connection

    def __enter__(self) -> MySqlClient:
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.rollback()
        self.close()
