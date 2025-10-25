import streamlit as st, pandas as pd, requests

st.set_page_config(page_title="Stock Alerts Demo", layout="wide")
st.title("📦 Intelligent Stock Alerts")

api = st.text_input("API base URL", "http://127.0.0.1:8000")
csv = st.file_uploader("Upload inventory CSV", type="csv")

with st.sidebar:
    st.caption("Demo controls")
    run_eval = st.button("Evaluate CSV")
    refresh = st.button("Refresh Open Alerts")
    run_esc = st.button("Run Escalations")

if csv and run_eval:
    df = pd.read_csv(csv)
    payload = df.to_dict(orient="records")
    r = requests.post(f"{api}/inventory", json=payload, timeout=10)
    st.subheader("Evaluation Results")
    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)

if refresh:
    st.subheader("Open Alerts")
    open_alerts = requests.get(f"{api}/alerts?status=open", timeout=10).json()
    st.dataframe(pd.DataFrame(open_alerts), use_container_width=True)

if run_esc:
    requests.post(f"{api}/escalations/run", timeout=10)
    st.success("Escalations processed.")
