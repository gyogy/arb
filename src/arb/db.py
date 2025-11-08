from __future__ import annotations

import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .flatten import Event, Odds


class OddsDatabase:
    def __init__(self, db_path: Optional[Union[str, Path]] = None) -> None:
        if isinstance(db_path, str) and db_path == ":memory:":
            self.db_path: Union[str, Path] = db_path
        else:
            base_path = Path(__file__).resolve().parents[2]
            if db_path:
                expanded = os.path.expanduser(os.path.expandvars(str(db_path)))
                resolved = Path(expanded)
            else:
                resolved = base_path / "odds.db"
            resolved.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = resolved

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()

    def __enter__(self) -> "OddsDatabase":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                sport TEXT NOT NULL,
                commence_time TEXT NOT NULL,
                home TEXT NOT NULL,
                away TEXT NOT NULL,
                outcome TEXT NOT NULL DEFAULT 'Unfinished' CHECK (
                    outcome IN ('Unfinished', 'Home', 'Away', 'Draw', 'No Contest')
                ),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                url TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                home_odds REAL,
                away_odds REAL,
                draw_odds REAL,
                captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (event_id, book_id, captured_at)
            );
            """
        )
        self.conn.commit()

    def save_event(self, event: "Event") -> None:
        self.conn.execute(
            """
            INSERT INTO events (id, sport, commence_time, home, away, outcome)
            VALUES (?, ?, ?, ?, ?, 'Unfinished')
            ON CONFLICT(id) DO UPDATE SET
                sport = excluded.sport,
                commence_time = excluded.commence_time,
                home = excluded.home,
                away = excluded.away,
                updated_at = CURRENT_TIMESTAMP
            """,
            (event.id, event.sport, event.commence_time, event.home, event.away),
        )

    def save_odds(self, odds_row: "Odds") -> None:
        book_id = self._upsert_book(odds_row.book_name, odds_row.book_url)
        captured_at = odds_row.last_update or datetime.now(timezone.utc).isoformat()

        self.conn.execute(
            """
            INSERT INTO odds (
                event_id,
                book_id,
                home_odds,
                away_odds,
                draw_odds,
                captured_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, book_id, captured_at) DO UPDATE SET
                home_odds = excluded.home_odds,
                away_odds = excluded.away_odds,
                draw_odds = excluded.draw_odds,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                odds_row.event_id,
                book_id,
                odds_row.home_odds,
                odds_row.away_odds,
                odds_row.draw_odds,
                captured_at,
            ),
        )

    def _upsert_book(self, name: str, url: Optional[str]) -> int:
        self.conn.execute(
            """
            INSERT INTO books (name, url)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                url = COALESCE(excluded.url, url),
                updated_at = CURRENT_TIMESTAMP
            """,
            (name, url),
        )
        cursor = self.conn.execute("SELECT id FROM books WHERE name = ?", (name,))
        book_id = cursor.fetchone()[0]
        return book_id

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
