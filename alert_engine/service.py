from datetime import datetime, timedelta
from typing import Dict, Any, List
from alert_engine.evaluator import compute_reorder_point, severity_band
from alert_engine.history import Store

DEFAULT_POLICY = [
    {"after_minutes": 0, "channels": ["console"]},
    {"after_minutes": 30, "channels": ["console", "email"]},
    {"after_minutes": 120, "channels": ["console", "email", "slack"]},
]

class AlertService:
    def __init__(self, store: Store, notifiers: Dict[str, Any], policy: List[dict] = None):
        self.store = store
        self.notifiers = notifiers
        self.policy = policy or DEFAULT_POLICY

    def _schedule_next(self, step_idx: int) -> str | None:
        if step_idx + 1 >= len(self.policy):
            return None
        mins = self.policy[step_idx + 1]["after_minutes"]
        return (datetime.utcnow() + timedelta(minutes=mins)).isoformat()

    def _send(self, alert_id: int, channels: List[str], subject: str, body: str):
        for ch in channels:
            adapter = self.notifiers.get(ch)
            if not adapter: continue
            try:
                adapter.send(subject, body)
                self.store.log_delivery(alert_id, ch, "sent")
            except Exception as e:
                self.store.log_delivery(alert_id, ch, "failed", 1, str(e))

    def evaluate_item(self, item: dict) -> dict:
        rop = compute_reorder_point(item["daily_demand"], item["lead_time_days"])
        band = severity_band(item["on_hand"], item.get("min_threshold", 0), rop)
        msg = f"{item['name']} (SKU:{item['sku']}) on_hand={item['on_hand']} | ROP={rop}"
        if band == "info":
            return {"sku": item["sku"], "severity": band, "alerted": False, "message": msg}

        aid = self.store.get_open_alert(item["sku"], item["location"], band)
        new_alert = False
        if aid is None:
            aid = self.store.create_alert(item["sku"], item["location"], band, msg)
            step_idx = 0
            new_alert = True
        else:
            cur = self.store.conn.execute("SELECT step_idx FROM alerts WHERE id=?", (aid,)).fetchone()
            step_idx = int(cur[0]) if cur else 0

        channels = self.policy[step_idx]["channels"]
        subject = f"{band.upper()} stock alert: {item['name']}"
        reco_qty = max(0, int((item['lead_time_days'] + 2) * item['daily_demand'] - item['on_hand']))
        body = msg + f"\nRecommended order qty: {reco_qty}"

        self._send(aid, channels, subject, body)
        self.store.mark_sent(aid, self._schedule_next(step_idx), step_idx)
        return {"sku": item["sku"], "severity": band, "alerted": True, "message": msg, "alert_id": aid, "new": new_alert}

    def run_due_escalations(self):
        for aid in self.store.due_escalations():
            row = self.store.conn.execute("SELECT step_idx, message, sku FROM alerts WHERE id=?", (aid,)).fetchone()
            if not row: continue
            step_idx, msg, sku = int(row[0]), row[1], row[2]
            next_step = step_idx + 1
            if next_step >= len(self.policy):
                continue
            channels = self.policy[next_step]["channels"]
            self._send(aid, channels, f"Escalation for {sku}", msg + "\n[Escalation]")
            self.store.mark_sent(aid, self._schedule_next(next_step), next_step)

    def ack(self, alert_id: int):
        self.store.update_status(alert_id, "acked")

    def resolve(self, alert_id: int):
        self.store.update_status(alert_id, "resolved")
