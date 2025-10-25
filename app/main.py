from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from alert_engine.history import Store
from alert_engine.service import AlertService
from alert_notifications.console_adapter import ConsoleAdapter

app = FastAPI(title="Stock Alerts", version="0.1.0")
store = Store("alerts.db")
notifiers = {"console": ConsoleAdapter()}
svc = AlertService(store, notifiers)

class InventoryItem(BaseModel):
    sku: str
    location: str
    name: str
    on_hand: int
    daily_demand: float
    lead_time_days: int
    min_threshold: int = 0

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/inventory")
def post_inventory(items: List[InventoryItem]):
    return [svc.evaluate_item(i.dict()) for i in items]

@app.get("/alerts")
def list_alerts(status: Optional[str] = None):
    q = "SELECT id, sku, location, severity_band, status, message, first_seen, last_sent, next_escalation, step_idx FROM alerts"
    args = []
    if status:
        q += " WHERE status=?"
        args.append(status)
    cur = store.conn.execute(q, tuple(args))
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

@app.post("/alerts/{alert_id}/ack")
def ack(alert_id: int):
    svc.ack(alert_id); return {"ok": True}

@app.post("/alerts/{alert_id}/resolve")
def resolve(alert_id: int):
    svc.resolve(alert_id); return {"ok": True}

@app.post("/escalations/run")
def run_escalations():
    svc.run_due_escalations(); return {"ok": True}
