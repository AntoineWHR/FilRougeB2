from __future__ import annotations

import sqlite3
from typing import Any, Iterable

from yops_portal.core.database import get_connection


class BaseRepository:
    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with get_connection() as db:
            return list(db.execute(query, tuple(params)).fetchall())

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        with get_connection() as db:
            return db.execute(query, tuple(params)).fetchone()

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        with get_connection() as db:
            cursor = db.execute(query, tuple(params))
            db.commit()
            return int(cursor.lastrowid)

