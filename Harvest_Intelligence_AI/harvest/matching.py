"""Deterministic preview: one stateless allocation run, source order, no orders placed."""
import pandas as pd
from .analytics import crop_balances
from .data import require_valid

ALLOCATION_COLUMNS = ["buyer_name", "buyer_type", "crop", "matched_kg",
                      "offer_price_per_kg", "transport_cost", "estimated_return_after_transport"]


def estimated_return(quantity, price, transport):
    import math
    if any(not math.isfinite(float(v)) or v < 0 for v in (quantity, price, transport)):
        raise ValueError("Financial inputs must be finite and non-negative.")
    # No allocation means no trip. Full quoted transport cost applies to a partial allocation.
    return round(quantity * price - transport, 2) if quantity > 0 else 0.0


def match_surplus(data, buyers):
    balances = crop_balances(data)
    buyers = require_valid(buyers, "buyers")
    remaining = {row.crop.casefold(): float(row.potential_surplus_kg)
                 for row in balances.itertuples()}
    records = []
    for buyer in buyers.itertuples():
        key = buyer.crop.casefold()
        quantity = min(remaining.get(key, 0.0), float(buyer.required_kg))
        if quantity <= 0:
            continue
        remaining[key] -= quantity
        records.append({"buyer_name": buyer.buyer_name, "buyer_type": buyer.buyer_type,
                        "crop": buyer.crop, "matched_kg": quantity,
                        "offer_price_per_kg": buyer.offer_price_per_kg,
                        "transport_cost": buyer.transport_cost,
                        "estimated_return_after_transport": estimated_return(
                            quantity, buyer.offer_price_per_kg, buyer.transport_cost)})
    balances["unmatched_kg"] = balances.crop.str.casefold().map(remaining)
    balances["matched_kg"] = balances.potential_surplus_kg - balances.unmatched_kg
    return pd.DataFrame(records, columns=ALLOCATION_COLUMNS), balances
