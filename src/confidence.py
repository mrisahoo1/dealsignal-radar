from dataclasses import dataclass
from .models import Company, Evidence
from .scoring import Score


@dataclass
class Confidence:
    evidence_confidence: float
    label: str
    factors: dict[str, float]
    independent_sources: int
    coverage: float
    limitations: list[str]


def evidence_confidence(company: Company, events: list[Evidence], score: Score, config: dict) -> Confidence:
    cfg = config["confidence"]
    expected = ("registry", "company", "ownership", "financial", "news")
    coverage = sum(company.coverage.get(k, False) for k in expected) / len(expected)
    missing = [k for k in expected if not company.coverage.get(k, False)]
    limitations = ["Missing source checks: " + ", ".join(missing)] if missing else []
    if not events:
        return Confidence(0, "Low", {}, 0, coverage * 100, ["No eligible evidence", *limitations])
    # Equal weight per source family, so a prolific publisher cannot dominate reliability.
    families = {e.source_family for e in events}
    quality = sum(max(c["quality"] for c in score.contributions if c["evidence"].source_family == f) for f in families) / len(families)
    recency = sum(max(c["recency"] for c in score.contributions if c["evidence"].source_family == f) for f in families) / len(families)
    positive = sum(max(0, c["values"][score.leading_type]) for c in score.contributions)
    negative = sum(max(0, -c["values"][score.leading_type]) for c in score.contributions)
    agreement = abs(positive - negative) / (positive + negative) if positive + negative else 1.0
    if positive and negative:
        limitations.append("Contradictory evidence for the leading transaction hypothesis")
    if not any(e.source_kind == "registry" for e in events):
        limitations.append("No direct registry evidence")
    if len(families) < 3:
        limitations.append(f"Only {len(families)} independent source {'family' if len(families) == 1 else 'families'}; confidence capped")
    factors = {"quality": quality, "independence": min(len(families) / cfg["source_target"], 1), "recency": recency, "breadth": min(len({c["rule"]["category"] for c in score.contributions}) / cfg["category_target"], 1), "agreement": agreement, "completeness": coverage}
    value = 100 * sum(factors[k] * w for k, w in cfg["weights"].items())
    if len(families) == 1:
        value = min(value, cfg["single_source_cap"])
    elif len(families) == 2:
        value = min(value, cfg["two_source_cap"])
    label = "High" if value >= cfg["high_threshold"] else "Medium" if value >= cfg["medium_threshold"] else "Low"
    return Confidence(round(value, 1), label, factors, len(families), coverage * 100, limitations)
