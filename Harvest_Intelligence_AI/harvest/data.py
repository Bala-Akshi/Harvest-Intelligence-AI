"""Explicit CSV mapping and strict validation. No silent imputation or row drops."""
from dataclasses import dataclass
import pandas as pd
import numpy as np

ALIASES = {
    "crop": ("crop", "crop_nm", "crop_name"),
    "available_kg": ("available_kg", "qty_avail", "available_quantity"),
    "estimated_demand_kg": ("estimated_demand_kg", "est_demand", "estimated_demand"),
    "market_price_per_kg": ("market_price_per_kg", "mkt_prc", "market_price"),
    "harvest_age_days": ("harvest_age_days", "harvest_age"),
}
BUYER_MAPPING = {"buyer_name": "buyer_name", "buyer_type": "buyer_type",
                 "crop": "crop_nm", "required_kg": "required_qty",
                 "offer_price_per_kg": "offer_price", "transport_cost": "transport_cost"}

@dataclass
class ValidationResult:
    data: pd.DataFrame | None
    errors: list[str]
    warnings: list[str]
    summary: dict


def suggest_mapping(columns):
    lookup = {str(c).strip().casefold(): c for c in columns}
    return {target: next((lookup[a] for a in aliases if a in lookup), None)
            for target, aliases in ALIASES.items()}


def validate_frame(raw, mapping, kind="agriculture"):
    if kind not in ("agriculture", "buyers"):
        raise ValueError("Unknown dataset kind")
    fields = list(ALIASES) if kind == "agriculture" else list(BUYER_MAPPING)
    summary = {"input_rows": len(raw), "valid_rows": 0, "invalid_rows": 0,
               "duplicate_rows": 0, "missing_cells": int(raw.isna().sum().sum())}
    errors, warnings = [], []
    if raw.empty:
        errors.append("Dataset has no records.")
    if raw.columns.duplicated().any():
        errors.append("Duplicate source column names are not allowed.")
    sources = [mapping.get(f) for f in fields]
    if any(s is None or s not in raw.columns for s in sources):
        errors.append("Map every required field to an existing source column.")
    if len(set(sources)) != len(sources):
        errors.append("Each source column can map to only one field.")
    if errors:
        return ValidationResult(None, errors, warnings, summary)
    data = raw[sources].copy()
    data.columns = fields
    text_fields = ["crop"] if kind == "agriculture" else ["crop", "buyer_name", "buyer_type"]
    bad = pd.Series(False, index=data.index)
    for f in text_fields:
        data[f] = data[f].astype("string").str.strip()
        missing = data[f].isna() | data[f].eq("")
        if missing.any():
            errors.append(f"{f}: {int(missing.sum())} blank value(s).")
        bad |= missing
    for f in set(fields) - set(text_fields):
        data[f] = pd.to_numeric(data[f], errors="coerce")
        invalid = data[f].isna() | ~np.isfinite(data[f]) | data[f].lt(0)
        if invalid.any():
            errors.append(f"{f}: {int(invalid.sum())} value(s) must be finite, numeric and non-negative.")
        bad |= invalid
    # One record per crop for Phase 1; batch-level aggregation is a future feature.
    identities = ["crop"] if kind == "agriculture" else ["buyer_name", "crop"]
    keys = data[identities].apply(lambda s: s.str.casefold())
    duplicate = keys.duplicated(keep=False)
    summary["duplicate_rows"] = int(duplicate.sum())
    if duplicate.any():
        errors.append("Duplicate crop or buyer/crop identities: merge or remove duplicates explicitly.")
        bad |= duplicate
    summary["invalid_rows"] = int(bad.sum())
    summary["valid_rows"] = int((~bad).sum())
    if len(raw.columns) > len(fields):
        warnings.append("Unmapped extra columns are excluded from calculations.")
    return ValidationResult(None if errors else data.reset_index(drop=True), errors, warnings, summary)


def require_valid(frame, kind="agriculture"):
    fields = list(ALIASES) if kind == "agriculture" else list(BUYER_MAPPING)
    result = validate_frame(frame, {f: f for f in fields}, kind)
    if result.errors:
        raise ValueError(" ".join(result.errors))
    return result.data
