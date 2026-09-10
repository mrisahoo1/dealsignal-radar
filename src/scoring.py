import math
from dataclasses import dataclass
from datetime import date
from .models import Evidence

TRANSACTIONS = {"sale_buyout": "Sale / Acquisition / Buyout", "ipo": "IPO", "refinancing": "Refinancing / Recapitalisation"}


@dataclass
class Score:
    transaction_propensity: float
    likely_type: str | None
    leading_type: str
    subscores: dict[str, float]
    contributions: list[dict]
    interactions: list[dict]


def recency_decay(age_days: int, half_life_days: float) -> float:
    if half_life_days <= 0:
        raise ValueError("Half life must be positive")
    if age_days < 0:
        raise ValueError("Future evidence cannot be scored")
    return math.exp(-math.log(2) * age_days / half_life_days)


def score_events(events: list[Evidence], as_of: date, config: dict) -> Score:
    """Input must be eligible and deduplicated. Output is an index, never a probability."""
    totals = dict.fromkeys(TRANSACTIONS, 0.0)
    contributions = []
    for event in events:
        rule = config["signals"][event.signal_type]
        quality = config["source_quality"][event.source_kind]
        recency = recency_decay((as_of - event.event_date).days, config["half_life_days"])
        base = rule["weight"] * rule["direction"] * event.strength * quality * recency
        values = {kind: base * rule["relevance"][kind] for kind in totals}
        for kind, value in values.items():
            totals[kind] += value
        contributions.append({"evidence": event, "rule": rule, "quality": quality, "recency": recency, "values": values})
    interactions = []
    for rule in config["interactions"]:
        left = [c for c in contributions if c["evidence"].signal_type == rule["signals"][0]]
        right = [c for c in contributions if c["evidence"].signal_type == rule["signals"][1]]
        pairs = [(a, b) for a in left for b in right if a["evidence"].source_family != b["evidence"].source_family and a["evidence"].event_id != b["evidence"].event_id]
        if pairs:
            a, b = max(pairs, key=lambda pair: min(c["quality"] * c["recency"] * c["evidence"].strength for c in pair))
            bonus = rule["bonus"] * min(c["quality"] * c["recency"] * c["evidence"].strength for c in (a, b))
            totals[rule["transaction"]] += bonus
            interactions.append({"name": rule["name"], "transaction": rule["transaction"], "value": bonus, "evidence_ids": [a["evidence"].id, b["evidence"].id]})
    subscores = {kind: max(0.0, round(100 * (-math.expm1(-max(total, 0) / config["normalization_scale"])), 1)) for kind, total in totals.items()}
    leading = max(subscores, key=subscores.get)
    propensity = subscores[leading]
    return Score(propensity, leading if propensity >= config["supported_type_minimum"] else None, leading, subscores, contributions, interactions)

