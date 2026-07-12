"""
PhonePe Pulse ETL Pipeline
Extracts all 9 dataset types (aggregated/map/top x transaction/user/insurance)
from a local clone of https://github.com/PhonePe/pulse, cleans them, and loads
them into SQLite + exports clean CSVs for Power BI / Streamlit.

USAGE:
    python extract_pipeline.py --pulse-dir ./pulse/data --out-dir ./processed
"""

import os
import json
import sqlite3
import logging
import argparse
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ---------- generic walker ----------

def walk_state_year_quarter(base_dir: Path):
    """Yields (state, year, quarter, json_data) for every file under base_dir,
    skipping and logging any file that is missing or corrupt instead of crashing."""
    if not base_dir.exists():
        log.warning(f"Path not found, skipping entirely: {base_dir}")
        return
    for state_dir in sorted(base_dir.iterdir()):
        if not state_dir.is_dir():
            continue
        for year_dir in sorted(state_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            for file in sorted(year_dir.glob("*.json")):
                quarter = file.stem
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    log.warning(f"Skipping unreadable file {file}: {e}")
                    continue
                yield state_dir.name, year_dir.name, quarter, data


# ---------- per-dataset extractors ----------

def extract_agg_transaction(data, state, year, quarter):
    rows = []
    for item in (data.get("data", {}) or {}).get("transactionData") or []:
        name = item.get("name")
        for pi in item.get("paymentInstruments") or []:
            rows.append(dict(state=state, year=year, quarter=quarter,
                              transaction_type=name, count=pi.get("count"),
                              amount=pi.get("amount")))
    return rows


def extract_agg_user(data, state, year, quarter):
    rows = []
    for item in (data.get("data", {}) or {}).get("usersByDevice") or []:
        rows.append(dict(state=state, year=year, quarter=quarter,
                          brand=item.get("brand"), count=item.get("count"),
                          percentage=item.get("percentage")))
    return rows


def extract_agg_insurance(data, state, year, quarter):
    return extract_agg_transaction(data, state, year, quarter)  # same shape


def extract_map_transaction(data, state, year, quarter):
    rows = []
    for item in (data.get("data", {}) or {}).get("hoverDataList") or []:
        district = item.get("name")
        for m in item.get("metric") or []:
            rows.append(dict(state=state, year=year, quarter=quarter,
                              district=district, metric_type=m.get("type"),
                              count=m.get("count"), amount=m.get("amount")))
    return rows


def extract_map_user(data, state, year, quarter):
    rows = []
    hover = (data.get("data", {}) or {}).get("hoverData") or {}
    for district, vals in hover.items():
        rows.append(dict(state=state, year=year, quarter=quarter,
                          district=district,
                          registered_users=vals.get("registeredUsers"),
                          app_opens=vals.get("appOpens")))
    return rows


def extract_map_insurance(data, state, year, quarter):
    return extract_map_transaction(data, state, year, quarter)  # same shape


def extract_top_transaction(data, state, year, quarter):
    rows = []
    d = data.get("data", {}) or {}
    for level in ("states", "districts", "pincodes"):
        for item in d.get(level) or []:
            entity = item.get("entityName") or item.get("name")
            metric = item.get("metric") or {}
            rows.append(dict(state=state, year=year, quarter=quarter,
                              level=level[:-1], entity=entity,
                              metric_type=metric.get("type"),
                              count=metric.get("count"), amount=metric.get("amount")))
    return rows


def extract_top_user(data, state, year, quarter):
    rows = []
    d = data.get("data", {}) or {}
    for level in ("states", "districts", "pincodes"):
        for item in d.get(level) or []:
            rows.append(dict(state=state, year=year, quarter=quarter,
                              level=level[:-1], entity=item.get("name"),
                              registered_users=item.get("registeredUsers")))
    return rows


def extract_top_insurance(data, state, year, quarter):
    return extract_top_transaction(data, state, year, quarter)  # same shape


# ---------- config: table_name -> (relative path under pulse/data, extractor) ----------

DATASETS = {
    "agg_transaction": ("aggregated/transaction/country/india/state", extract_agg_transaction),
    "agg_user":        ("aggregated/user/country/india/state", extract_agg_user),
    "agg_insurance":   ("aggregated/insurance/country/india/state", extract_agg_insurance),
    "map_transaction": ("map/transaction/hover/country/india/state", extract_map_transaction),
    "map_user":        ("map/user/hover/country/india/state", extract_map_user),
    "map_insurance":   ("map/insurance/hover/country/india/state", extract_map_insurance),
    "top_transaction": ("top/transaction/country/india/state", extract_top_transaction),
    "top_user":        ("top/user/country/india/state", extract_top_user),
    "top_insurance":   ("top/insurance/country/india/state", extract_top_insurance),
}


def build_table(pulse_dir: Path, rel_path: str, extractor) -> pd.DataFrame:
    base = pulse_dir / rel_path
    rows = []
    for state, year, quarter, data in walk_state_year_quarter(base):
        rows.extend(extractor(data, state, year, quarter))
    df = pd.DataFrame(rows)
    if df.empty:
        log.warning(f"No rows extracted from {base}")
        return df
    before = len(df)
    df = df.drop_duplicates()
    if len(df) != before:
        log.info(f"Dropped {before - len(df)} duplicate rows")
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulse-dir", default="pulse/data",
                         help="Path to the cloned PhonePe/pulse repo's data folder")
    parser.add_argument("--out-dir", default="processed",
                         help="Where to write CSVs and the SQLite DB")
    args = parser.parse_args()

    pulse_dir = Path(args.pulse_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    db_path = out_dir / "phonepe.db"
    conn = sqlite3.connect(db_path)

    try:
        for table_name, (rel_path, extractor) in DATASETS.items():
            log.info(f"Building {table_name} ...")
            df = build_table(pulse_dir, rel_path, extractor)
            if df.empty:
                continue
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            df.to_csv(out_dir / f"{table_name}.csv", index=False)
            log.info(f"  -> {len(df):,} rows written to table '{table_name}' and CSV")
    finally:
        conn.close()

    log.info(f"Done. SQLite DB at {db_path}, CSVs in {out_dir}/")


if __name__ == "__main__":
    main()
