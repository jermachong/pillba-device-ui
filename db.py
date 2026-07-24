from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


DB_PATH = Path(__file__).with_name("pillba.sqlite3")


@dataclass(frozen=True)
class Medication:
    id: int | None
    name: str
    dose: str
    slot: int
    hour: int
    minute: int
    days_mask: int = 127
    active: int = 1


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(path: Path = DB_PATH) -> None:
    connection = connect(path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dose TEXT NOT NULL,
                slot INTEGER NOT NULL,
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,
                days_mask INTEGER NOT NULL DEFAULT 127,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot INTEGER NOT NULL,
                medication TEXT NOT NULL,
                event_time INTEGER NOT NULL,
                status INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        _seed_defaults(connection)
        connection.commit()
    finally:
        connection.close()


def _seed_defaults(connection: sqlite3.Connection) -> None:
    defaults = {
        "volume": "70",
        "refill_alert": "1",
        "wifi": "1",
        "bluetooth": "0",
        "timezone": "UTC+0",
    }
    for key, value in defaults.items():
        connection.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )


def list_medications(path: Path = DB_PATH) -> list[Medication]:
    connection = connect(path)
    try:
        rows = connection.execute(
            "SELECT id, name, dose, slot, hour, minute, days_mask, active FROM medications ORDER BY slot"
        ).fetchall()
        return [Medication(**dict(row)) for row in rows]
    finally:
        connection.close()


def upsert_medication(medication: Medication, path: Path = DB_PATH) -> None:
    connection = connect(path)
    try:
        if medication.id is None:
            connection.execute(
                """
                INSERT INTO medications (name, dose, slot, hour, minute, days_mask, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    medication.name,
                    medication.dose,
                    medication.slot,
                    medication.hour,
                    medication.minute,
                    medication.days_mask,
                    medication.active,
                ),
            )
        else:
            connection.execute(
                """
                UPDATE medications
                SET name = ?, dose = ?, slot = ?, hour = ?, minute = ?, days_mask = ?, active = ?
                WHERE id = ?
                """,
                (
                    medication.name,
                    medication.dose,
                    medication.slot,
                    medication.hour,
                    medication.minute,
                    medication.days_mask,
                    medication.active,
                    medication.id,
                ),
            )
        connection.commit()
    finally:
        connection.close()


def fetch_setting(key: str, default: str = "") -> str:
    connection = connect()
    try:
        row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return default if row is None else str(row["value"])
    finally:
        connection.close()


def set_setting(key: str, value: str) -> None:
    connection = connect()
    try:
        connection.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        connection.commit()
    finally:
        connection.close()
