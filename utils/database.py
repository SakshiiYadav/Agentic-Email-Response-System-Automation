"""
DatabaseManager — SQLite-backed persistence
Stores processed emails with full pipeline metadata for audit trail.
"""

import sqlite3
import json
import os
from datetime import datetime


DB_PATH = "email_agent.db"


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender          TEXT,
                    subject         TEXT,
                    body            TEXT,
                    timestamp       TEXT,
                    sentiment       TEXT,
                    priority        TEXT,
                    urgency_score   INTEGER,
                    category        TEXT,
                    escalation_required INTEGER,
                    key_issues      TEXT,
                    rag_context     TEXT,
                    response_draft  TEXT,
                    tone_used       TEXT,
                    confidence      REAL,
                    review_notes    TEXT,
                    approved        INTEGER,
                    scheduled_time  TEXT,
                    delay_minutes   INTEGER,
                    processed_at    TEXT
                )
            """)
            conn.commit()

    def save_batch(self, emails: list):
        with self._conn() as conn:
            for e in emails:
                conn.execute("""
                    INSERT INTO emails (
                        sender, subject, body, timestamp,
                        sentiment, priority, urgency_score, category,
                        escalation_required, key_issues, rag_context,
                        response_draft, tone_used, confidence, review_notes,
                        approved, scheduled_time, delay_minutes, processed_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    e.get("sender",""),
                    e.get("subject",""),
                    e.get("body",""),
                    e.get("timestamp",""),
                    e.get("sentiment",""),
                    e.get("priority",""),
                    e.get("urgency_score",0),
                    e.get("category",""),
                    int(e.get("escalation_required",False)),
                    json.dumps(e.get("key_issues",[])),
                    json.dumps(e.get("rag_context",[])),
                    e.get("response_draft",""),
                    e.get("tone_used",""),
                    e.get("confidence",0.0),
                    e.get("review_notes",""),
                    int(e.get("approved",False)),
                    e.get("scheduled_time",""),
                    e.get("delay_minutes",0),
                    datetime.now().isoformat(),
                ))
            conn.commit()

    def fetch_all(self) -> list:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM emails ORDER BY processed_at DESC").fetchall()
        return rows
