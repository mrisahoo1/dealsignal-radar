import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from .models import Company, Evidence

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    return json.loads((ROOT / "config/signal_weights.json").read_text(encoding="utf-8-sig"))


def load_fixtures(directory: Path = ROOT / "data") -> tuple[list[Company], list[Evidence]]:
    with (directory / "companies.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    companies = []
    for row in rows:
        row["coverage"] = json.loads(row["coverage"])
        companies.append(Company.model_validate(row))
    events = [Evidence.model_validate(row) for row in json.loads((directory / "evidence.json").read_text(encoding="utf-8-sig"))]
    ids = [c.id for c in companies]
    if len(set(ids)) != len(ids) or len({e.id for e in events}) != len(events):
        raise ValueError("Company and evidence IDs must be unique")
    signals = load_config()["signals"]
    for event in events:
        if event.company_id not in ids or event.signal_type not in signals:
            raise ValueError(f"Unresolved company or unknown signal: {event.id}")
    return companies, events


def eligible(events: list[Evidence], as_of: date) -> list[Evidence]:
    return [e for e in events if max(e.event_date, e.published_date, e.observed_date) <= as_of]


def deduplicate(events: list[Evidence], config: dict) -> tuple[list[Evidence], dict[str, list[Evidence]]]:
    """Merge canonical events and exact normalized text copies; retain all lineage.

    Same URL alone is not enough: a document may contain several different signals.
    Production must add semantic clustering and human review of entity/event merges.
    """
    groups: list[list[Evidence]] = []
    keys: list[set] = []
    for event in sorted(events, key=lambda e: e.id):
        fingerprint = hashlib.sha256(re.sub(r"\W+", "", event.supporting_evidence.lower()).encode()).hexdigest()
        event_keys = {(event.company_id, "event", event.event_id), (event.company_id, "text", event.signal_type, fingerprint)}
        matches = [i for i, existing in enumerate(keys) if event_keys & existing]
        group = [event]
        for i in reversed(matches):
            group.extend(groups.pop(i))
            event_keys |= keys.pop(i)
        groups.append(group)
        keys.append(event_keys)
    representatives, lineage = [], {}
    for group in groups:
        # Earliest record among equally credible sources prevents syndication refreshing age.
        representative = min(group, key=lambda e: (not e.is_original, -config["source_quality"][e.source_kind], e.published_date, e.id))
        representatives.append(representative)
        lineage[representative.id] = sorted(group, key=lambda e: (e.published_date, e.id))
    return sorted(representatives, key=lambda e: (e.event_date, e.id), reverse=True), lineage

