# Capstone: Intelligent Stock Alert System

This project implements a minimal alerting service for low stock levels with restocking recommendations.
It includes threshold detection, de-duplication, escalation policy, delivery adapters, alert history tables, and a small API/UI for demos.

## Features
- Threshold-based alerts with simple ROP (reorder point) logic
- De-duplication (one open alert per SKU/location/severity band)
- Step-based escalation policy (console → email → slack)
- Delivery logging (success/failure) and alert event history
- REST API (FastAPI) and optional demo UI (Streamlit)

## Quickstart (API)
```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
# Visit http://127.0.0.1:8000/docs
```

## Demo UI (Streamlit)
```bash
streamlit run app/streamlit_app.py
```

## API Endpoints
- `POST /inventory` — Evaluate list of inventory items for alerts
- `GET /alerts?status=open` — List alerts (filter by status)
- `POST /alerts/{id}/ack` — Acknowledge an alert
- `POST /alerts/{id}/resolve` — Resolve an alert
- `POST /escalations/run` — Process due escalations

## CSV Columns (for Streamlit)
`sku,location,name,on_hand,daily_demand,lead_time_days,min_threshold`

## Notes
- SQLite file `alerts.db` is created in the working directory.
- Email/Slack adapters are included but disabled by default; configure them in `app/main.py`.
