# Harvest Intelligence AI — Phase 1

Functional local Python/Streamlit foundation. No API key or paid service is required. All displayed totals come from validated data and calculation functions.

## Exact Windows VS Code commands

Install Python 3.11 or 3.12 and the VS Code Python extension. Extract the ZIP to `C:\Harvest_Intelligence_AI_Phase1`. The ZIP contains the project folder `Harvest_Intelligence_AI`.

In **VS Code → Terminal → New Terminal**, select **Command Prompt** and run:

```bat
cd /d C:\Harvest_Intelligence_AI_Phase1\Harvest_Intelligence_AI
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

If using Python 3.12, replace `py -3.11` with `py -3.12`. Open http://localhost:8501. Press Ctrl+C to stop. In VS Code, run **Python: Select Interpreter** and select `.venv\Scripts\python.exe`.

PowerShell alternative (activation is unnecessary):

```powershell
Set-Location C:\Harvest_Intelligence_AI_Phase1\Harvest_Intelligence_AI
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

SQLite comes with Python; do not install it with pip. Initial dependency installation needs internet. Normal use runs locally. Requirements use bounded ranges; `requirements-tested.txt` records the exact tested direct dependency versions.

## Phase 1 walkthrough

1. Start on Home; download either demo CSV if needed.
2. Click **Load demo data** in the sidebar.
3. Select Dashboard: 3 records, 1,050 kg available, 850 kg estimated demand, 250 kg positive surplus, 50 kg shortage.
4. Alternatively select Upload Data, choose `data/agriculture_demo.csv`, inspect automatic suggestions, edit mappings if needed, then **Validate and activate**.
5. Navigate among pages: the same validated dataset remains active. Invalid uploads never replace the prior active dataset.
6. Change language to Tamil to show bilingual navigation, KPI and core control labels. Technical schema fields, validation messages and explanatory prose currently remain English.
7. Optionally save a snapshot, restart, then restore it. Snapshots are never loaded automatically into a new browser session.

## Delivered scope

| Screen | Phase 1 status |
|---|---|
| Home | Working introduction and demo downloads |
| Upload Data | Working agriculture CSV reader, editable mapping and strict validation summary |
| Dashboard | Working foundation: calculated KPIs, grouped chart and balances table |
| Surplus and Risk | Navigation scaffold only |
| Buyer Matching | Navigation scaffold only; tested matching functions ready |
| Profit Analysis | Navigation scaffold only; tested return function ready |
| AI Assistant | Navigation scaffold only |

This phase does **not** claim the full five-minute judging demo passes. Risk scoring, buyer-upload workflow, financial comparison UI and grounded assistant responses are later phases. No later phase has been started. The sample-calculation acceptance contract is tested now.

## Calculation and allocation contract

- Agriculture quantities and demand: kg. Prices: INR per kg. Harvest age: days. Transport: INR per allocated buyer trip.
- Potential surplus per crop = `max(available_kg - estimated_demand_kg, 0)`.
- Shortage per crop = `max(estimated_demand_kg - available_kg, 0)`.
- Sum positive crop surpluses separately from shortages. Net supply minus demand (200 kg here) is not the 250 kg positive-surplus KPI.
- Demand is the **uploaded estimate**, not a trained-model forecast. No forecasts or live prices exist in Phase 1.
- Matching is a stateless preview in buyer CSV row order. Match `min(remaining crop surplus, buyer required kg)`. Each buyer/crop identity occurs once; duplicate identities are rejected. Repeating a run recomputes rather than appends allocations. Crop matching ignores case and surrounding whitespace.
- No buyer opportunity is a confirmed order. No ordering or reservation occurs.
- Estimated return after transport = `matched_kg * offer_price_per_kg - transport_cost`. Charge the full quoted cost once, including partial allocations. Zero allocations incur no trip/cost. Negative returns remain visible; no silent clamping.
- These are **returns after transport, not profit**: production, storage, packaging, spoilage, taxes and other costs are unknown. No rounded KPI constants are stored in application code.

| Sample check | Expected |
|---|---:|
| Records | 3 |
| Available | 1,050 kg |
| Uploaded estimated demand | 850 kg |
| Positive crop surpluses | 250 kg |
| Crop shortages | 50 kg |
| Tomato surplus | 200 kg |
| Tomato potential matches / unmatched | 180 / 20 kg |
| Green Leaf return after transport | ₹2,600 |
| City Hostel return after transport | ₹1,830 |
| Combined tomato buyer return | ₹4,430 |

The Onion buyer requests 100 kg but can match only 50 kg surplus; its estimated return is `50 * 32 - 180 = ₹1,420`.

## Data validation

The supplied abbreviated headers map to a stable internal schema. Suggestion aliases are explicit and case-insensitive; uncertain columns require manual mapping. Required numeric cells must be finite and non-negative. Blank crop names, missing fields, missing prices, malformed numbers, duplicate columns, duplicate crop rows or duplicate buyer/crop identities are rejected. Zero quantities/prices are allowed. Decimal quantities are allowed. No demand, price or missing value is invented. Extra columns are excluded with a warning. Phase 1 accepts one row per crop; combine genuine batches deliberately before uploading. No silent duplicate dropping or partial invalid-row activation occurs.

CSV limit: 10 MB, UTF-8/UTF-8-BOM, comma delimited. Quality summary reports input rows, valid rows, invalid rows, missing cells and duplicate identity rows. Missing-cell count covers the raw input; valid/invalid rows concern the mapped fields. Buyer CSV validation is available as a module, not yet as a UI workflow.

## Project layout

```text
Harvest_Intelligence_AI/
  app.py                         Streamlit shell and phase-1 screens
  harvest/
    data.py                      Mapping and validation
    analytics.py                 KPIs and crop balances
    matching.py                  Capped allocation and transport returns
    storage.py                   SQLite snapshot foundation
    i18n.py                      English/Tamil labels
  data/
    agriculture_demo.csv
    buyers_demo.csv
  tests/
    conftest.py
    test_calculations.py
    test_validation_storage.py
    test_app.py
  docs/PHASES.md
  .streamlit/config.toml
  requirements.txt
  requirements-tested.txt
  pytest.ini
  README.md
```

Session State is the active dataset source for every screen; it persists across navigation and reruns in that browser session. A new session starts empty. SQLite saves one explicit active agriculture snapshot at `data/harvest.sqlite3`; buyer/assistant histories are not implemented. Set `HARVEST_DB_PATH` to override the database path. Do not run this local single-user scaffold as a public multi-user service without adding authentication and per-user storage isolation.

## Verification

`python -m pytest -q` checks all mandatory sample numbers, no netting of shortages, partial fills and caps, duplicate rejection, repeated runs, zero/negative returns, malformed inputs, missing values, empty input, mapping edits, SQLite round-trip/atomic rejection, entry point, navigation, Tamil labels and shared demo state using Streamlit AppTest. Tests do not require real-time data, models or external APIs. Browser-specific mobile rendering and file-picker interaction still require manual checks.

Framework testing reference: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
