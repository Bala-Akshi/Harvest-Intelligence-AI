"""SQLite foundation. One atomic active snapshot, no uploaded file SQL interpolation."""
import json
import sqlite3
from pathlib import Path
import pandas as pd
from .data import require_valid


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE IF NOT EXISTS active_dataset "
                "(id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL, source TEXT NOT NULL)")
    return con


def save_snapshot(data, source, path):
    data = require_valid(data)
    con = connect(path)
    try:
        with con:
            con.execute("INSERT OR REPLACE INTO active_dataset VALUES (1, ?, ?)",
                        (data.to_json(orient="records"), source))
    finally:
        con.close()


def load_snapshot(path):
    con = connect(path)
    try:
        row = con.execute("SELECT payload, source FROM active_dataset WHERE id=1").fetchone()
        return (require_valid(pd.DataFrame(json.loads(row[0]))), row[1]) if row else None
    finally:
        con.close()
