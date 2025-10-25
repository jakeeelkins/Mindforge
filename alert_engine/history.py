import sqlite3
from datetime import datetime
from typing import Optional

DDL = """
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sku TEXT NOT NULL,
  location TEXT NOT NULL,
  severity_band TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open',
  message TEXT NOT NULL,
  first_seen TEXT NOT NULL,
  last_sent TEXT,
  next_escalation TEXT,
  step_idx INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_alert_open ON alerts(sku, location, severity_band, status);
CREATE TABLE IF NOT EXISTS alert_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alert_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  action TEXT NOT NULL,
  meta TEXT
);
CREATE TABLE IF NOT EXISTS deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alert_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  channel TEXT NOT NULL,
  status TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 1,
  last_error TEXT
);
"""

class Store:
    def __init__(self, path: str = "alerts.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.executescript(DDL)
        self.conn.commit()

    def get_open_alert(self, sku: str, location: str, band: str):
        cur = self.conn.execute(
            "SELECT id FROM alerts WHERE sku=? AND location=? AND severity_band=? AND status='open'",
            (sku, location, band))
        r = cur.fetchone()
        return None if not r else r[0]

    def create_alert(self, sku: str, location: str, band: str, message: str) -> int:
        now = datetime.utcnow().isoformat()
        cur = self.conn.execute(
            "INSERT INTO alerts(sku,location,severity_band,status,message,first_seen) VALUES (?,?,?,?,?,?)",
            (sku, location, band, "open", message, now))
        self.conn.commit()
        aid = cur.lastrowid
        self.add_event(aid, "created", message)
        return aid

    def update_status(self, alert_id: int, status: str):
        self.conn.execute("UPDATE alerts SET status=? WHERE id=?", (status, alert_id))
        self.conn.commit()
        self.add_event(alert_id, status, None)

    def mark_sent(self, alert_id: int, next_escalation: Optional[str], step_idx: int):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "UPDATE alerts SET last_sent=?, next_escalation=?, step_idx=? WHERE id=?",
            (now, next_escalation, step_idx, alert_id)
        )
        self.conn.commit()
        self.add_event(alert_id, "notified", None)

    def add_event(self, alert_id: int, action: str, meta: Optional[str]):
        self.conn.execute("INSERT INTO alert_events(alert_id, ts, action, meta) VALUES (?,?,?,?)",
                          (alert_id, datetime.utcnow().isoformat(), action, meta))
        self.conn.commit()

    def log_delivery(self, alert_id: int, channel: str, status: str, attempts: int = 1, last_error: str | None = None):
        self.conn.execute(
            "INSERT INTO deliveries(alert_id, ts, channel, status, attempts, last_error) VALUES (?,?,?,?,?,?)",
            (alert_id, datetime.utcnow().isoformat(), channel, status, attempts, last_error))
        self.conn.commit()

    def due_escalations(self):
        cur = self.conn.execute(
            "SELECT id FROM alerts WHERE status='open' AND next_escalation IS NOT NULL AND next_escalation <= ?",
            (datetime.utcnow().isoformat(),))
        return [r[0] for r in cur.fetchall()]
