"""Phase 1 entry point. Start with: python -m streamlit run app.py"""
import hashlib
import os
import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from harvest.analytics import calculate_kpis, crop_balances
from harvest.data import suggest_mapping, validate_frame
from harvest.i18n import label
from harvest.storage import load_snapshot, save_snapshot

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get("HARVEST_DB_PATH", str(ROOT / "data" / "harvest.sqlite3")))
PAGES = ["Home", "Upload Data", "Dashboard", "Surplus and Risk", "Buyer Matching", "Profit Analysis", "AI Assistant"]
st.set_page_config(page_title="Harvest Intelligence AI", layout="wide")
language = st.sidebar.selectbox("Language / மொழி", ["English", "தமிழ்"], key="language")
def t(text):
    return label(text, language)

st.sidebar.title("HARVEST")
st.sidebar.caption("INTELLIGENCE AI · PHASE 1")
page = st.sidebar.radio(t("Navigation"), PAGES, format_func=t, key="navigation")
st.session_state.setdefault("active_data", None)
st.session_state.setdefault("source", "No active dataset")

if st.sidebar.button(t("Load demo data"), key="load_demo", use_container_width=True):
    result = validate_frame(pd.read_csv(ROOT / "data/agriculture_demo.csv"),
                            suggest_mapping(pd.read_csv(ROOT / "data/agriculture_demo.csv").columns))
    if result.errors:
        st.error(" ".join(result.errors))
    else:
        st.session_state.active_data = result.data
        st.session_state.source = "Sample agriculture demo"

if st.sidebar.button(t("Restore local snapshot")):
    try:
        snapshot = load_snapshot(DB)
        if snapshot:
            st.session_state.active_data, st.session_state.source = snapshot
        else:
            st.sidebar.info("No saved snapshot / சேமித்த தரவு இல்லை")
    except (OSError, ValueError, sqlite3.Error) as exc:
        st.sidebar.error(f"Could not restore: {exc}")

active = st.session_state.active_data
st.sidebar.caption(f"Source / தரவு மூலம்: {st.session_state.source}")
if active is not None and st.sidebar.button(t("Save local snapshot")):
    try:
        save_snapshot(active, st.session_state.source, DB)
        st.sidebar.success("Saved / சேமிக்கப்பட்டது")
    except (OSError, ValueError, sqlite3.Error) as exc:
        st.sidebar.error(f"Could not save: {exc}")

st.title("Harvest Intelligence AI")
st.caption("Agricultural records → practical selling decisions / வேளாண் தரவிலிருந்து விற்பனை முடிவுகள்")
st.header(t(page))

if page == "Home":
    st.subheader("Understand availability. Plan your next sale.")
    st.write("Farmers can have produce available yet face losses without visibility into demand, buyers, and transport costs.")
    st.info("Phase 1: working scaffold, validated CSV loading, shared active data, dashboard preview and tested calculation foundations.")
    st.write("Start: load the demo from the sidebar, then select Dashboard. Or select Upload Data to validate your CSV.")
    st.write("Uploaded demand remains an estimate. No model forecast or live market feed is generated.")
    for filename, title in [("agriculture_demo.csv", "Download agriculture sample"), ("buyers_demo.csv", "Download buyers sample")]:
        st.download_button(t(title), (ROOT / "data" / filename).read_bytes(), file_name=filename, mime="text/csv")
    st.caption("Buyer sample contains potential opportunities only; no confirmed orders. Figures are estimates, not guaranteed profit.")

elif page == "Upload Data":
    st.write("Units: kg, ₹/kg and harvest age in days. Required values must be finite and non-negative; crop names must be unique.")
    uploaded = st.file_uploader(t("Upload agriculture CSV"), type=["csv"])
    if uploaded:
        try:
            payload = uploaded.getvalue()
            if len(payload) > 10 * 1024 * 1024:
                raise ValueError("CSV exceeds the 10 MB limit.")
            raw = pd.read_csv(uploaded, encoding="utf-8-sig")
            # Pandas renames duplicate CSV headers; reject these before mapping.
            import csv, io
            headers = next(csv.reader(io.StringIO(payload.decode("utf-8-sig"))))
            if len(headers) != len(set(headers)):
                raise ValueError("Duplicate CSV headers are not allowed.")
            st.dataframe(raw.head(20), use_container_width=True)
            st.subheader(t("Column mapping"))
            suggestions = suggest_mapping(raw.columns)
            digest = hashlib.sha256(payload).hexdigest()[:12]
            mapping = {}
            with st.form(f"mapping_{digest}"):
                for target, source in suggestions.items():
                    options = [None] + list(raw.columns)
                    mapping[target] = st.selectbox(target, options, index=options.index(source),
                                                   format_func=lambda v: "Select column / தேர்ந்தெடு" if v is None else str(v),
                                                   key=f"{digest}_{target}")
                submitted = st.form_submit_button(t("Validate and activate"))
            if submitted:
                result = validate_frame(raw, mapping)
                st.subheader(t("Quality summary"))
                st.json(result.summary)
                for warning in result.warnings:
                    st.warning(warning)
                for error in result.errors:
                    st.error(error)
                if not result.errors:
                    st.session_state.active_data = result.data
                    st.session_state.source = f"Uploaded: {uploaded.name}"
                    st.success("Validated and active / சரிபார்க்கப்பட்டு பயன்பாட்டில் உள்ளது")
                else:
                    st.info("Fix the CSV or mapping and resubmit. Previous validated data stays active.")
        except (ValueError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError, StopIteration) as exc:
            st.error(f"Could not read CSV: {exc}")

elif page == "Dashboard":
    if active is None:
        st.info("Load demo data or validate an agriculture CSV first / முதலில் தரவை ஏற்றவும்")
    else:
        kpis = calculate_kpis(active)
        names = [("Uploaded records", "records"), ("Available (kg)", "available_kg"),
                 ("Estimated demand (kg)", "estimated_demand_kg"),
                 ("Potential surplus (kg)", "positive_surplus_kg"), ("Shortage (kg)", "shortage_kg")]
        for start in range(0, len(names), 3):
            columns = st.columns(min(3, len(names) - start))
            for col, (name, key) in zip(columns, names[start:start+3]):
                col.metric(t(name), f"{kpis[key]:,.0f}")
        balances = crop_balances(active)
        chart_data = balances.melt(id_vars="crop", value_vars=["available_kg", "estimated_demand_kg"],
                                   var_name="measure", value_name="kg")
        fig = px.bar(chart_data, x="crop", y="kg", color="measure", barmode="group",
                     labels={"crop": "Crop / பயிர்", "kg": "Quantity (kg) / அளவு", "measure": "Measure"},
                     color_discrete_sequence=["#166534", "#1E40AF"])
        st.plotly_chart(fig, use_container_width=True)
        st.subheader(t("Active validated data"))
        st.dataframe(balances, use_container_width=True, hide_index=True)
        st.caption("Surplus = max(available − uploaded estimated demand, 0), summed by crop. Shortages are calculated separately; they are never netted against surpluses.")
else:
    st.info("Planned screen / திட்டமிடப்பட்ட திரை. This screen is scaffolded only in Phase 1.")
    st.write("The active validated dataset is shared through session state. Detailed workflows will be added in later requested phases.")
    if active is not None:
        st.caption(f"Active records / நடப்புப் பதிவுகள்: {len(active)}")
