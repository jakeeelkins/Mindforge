from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import json
import random

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, HTTPException

router = APIRouter(prefix="/stock", tags=["Stock"])

# ---- mock catalog (replace with DB) ----
PRODUCTS = [
    {"id": "banana", "name": "Banana", "min_threshold": 20},
    {"id": "broccoli", "name": "Broccoli", "min_threshold": 12},
    {"id": "milk", "name": "Milk", "min_threshold": 15},
]

def _prod(product_id: str):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None

# ---- historical time-series (mock) ----
@router.get("/timeseries")
async def timeseries(
    product_id: str = Query(..., description="e.g., banana"),
    start: Optional[str] = Query(None, description="ISO date, default 24h ago"),
    end: Optional[str] = Query(None, description="ISO date, default now"),
) -> Dict[str, Any]:
    p = _prod(product_id)
    if not p:
        raise HTTPException(404, "Unknown product")

    end_dt = datetime.fromisoformat(end) if end else datetime.utcnow()
    start_dt = datetime.fromisoformat(start) if start else end_dt - timedelta(hours=24)

    # Generate hourly points between start/end
    points = []
    t = start_dt
    level = random.randint(30, 80)
    while t <= end_dt:
        # random walk for demo
        level = max(0, min(120, level + random.randint(-6, 6)))
        points.append({"ts": t.isoformat(), "level": level})
        t += timedelta(minutes=30)

    return {"product": p, "points": points}

# ---- current snapshot for all products (mock) ----
@router.get("/current")
async def current_levels() -> Dict[str, Any]:
    snapshot = []
    for p in PRODUCTS:
        level = random.randint(0, 120)
        snapshot.append({
            "product_id": p["id"],
            "name": p["name"],
            "level": level,
            "min_threshold": p["min_threshold"],
            "is_low": level < p["min_threshold"],
        })
    return {"snapshot": snapshot, "as_of": datetime.utcnow().isoformat()}

# ---- product catalog ----
@router.get("/products")
async def list_products() -> List[Dict[str, Any]]:
    return PRODUCTS

# ---- simple alerts feed (mock) ----
@router.get("/alerts")
async def alerts() -> List[Dict[str, Any]]:
    # Derive alerts from current snapshot for demo
    snap = await current_levels()
    out = []
    for row in snap["snapshot"]:
        if row["is_low"]:
            out.append({
                "product_id": row["product_id"],
                "message": f"{row['name']} low: {row['level']} (min {row['min_threshold']})",
                "severity": "warning",
                "ts": snap["as_of"],
            })
    return out

# ---- real-time over WebSocket (mock push every 3s) ----
@router.websocket("/ws")
async def stock_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            # push a small diff-like message
            payload = {"as_of": datetime.utcnow().isoformat(), "products": []}
            for p in PRODUCTS:
                payload["products"].append({
                    "product_id": p["id"],
                    "level": random.randint(0, 120),
                })
            await ws.send_text(json.dumps(payload))
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
