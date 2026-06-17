from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from utils.config_loader import ROOT_DIR


class DatabaseClient:
    """Small database helper for pytest setup, assertions, and cleanup."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.db_type = config.get("type", "sqlite")
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        if self.connection is not None:
            return

        if self.db_type != "sqlite":
            raise NotImplementedError(
                f"Unsupported database type: {self.db_type}. "
                "Current demo supports sqlite without extra dependencies."
            )

        database = self.config.get("database", "data/test.db")
        database_path = Path(database)
        if not database_path.is_absolute():
            database_path = ROOT_DIR / database_path

        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> int:
        connection = self._get_connection()
        cursor = connection.execute(sql, tuple(params or ()))
        connection.commit()
        return cursor.rowcount

    def execute_many(self, sql: str, params_list: Iterable[Iterable[Any]]) -> int:
        connection = self._get_connection()
        cursor = connection.executemany(sql, [tuple(params) for params in params_list])
        connection.commit()
        return cursor.rowcount

    def fetch_one(self, sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
        cursor = self._get_connection().execute(sql, tuple(params or ()))
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
        cursor = self._get_connection().execute(sql, tuple(params or ()))
        return [dict(row) for row in cursor.fetchall()]

    def _get_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            self.connect()
        if self.connection is None:
            raise RuntimeError("database connection is not initialized")
        return self.connection

    def __enter__(self) -> DatabaseClient:
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
