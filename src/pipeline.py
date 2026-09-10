from dataclasses import dataclass
from datetime import date
from .confidence import Confidence, evidence_confidence
from .ingestion import deduplicate, eligible
from .models import Company, Evidence, SignalStage
from .scoring import Score, score_events


@dataclass
class Assessment:
    company: Company
    score: Score
    confidence: Confidence
    events: list[Evidence]
    lineage: dict[str, list[Evidence]]
    priority: float
    action: str
    signal_stage: SignalStage
    rank: int = 0


def signal_stage(score: Score, as_of: date, config: dict) -> SignalStage:
    """Describe observed evidence maturity, independently of score magnitude.

    Reuse eligible, deduplicated contributions; negative/zero-weight evidence cannot
    advance a stage. Emerging must have no process-level record, even a weak/stale one.
    """
    cfg = config["stage_rules"]
    positive = [c for c in score.contributions if any(v > 0 for v in c["values"].values())]
    meaningful = [c for c in positive
                  if (as_of - c["evidence"].event_date).days <= cfg["max_age_days"]
                  and c["evidence"].strength >= cfg["minimum_strength"]
                  and c["quality"] >= cfg["minimum_source_quality"]]
    if any(c["rule"].get("process_level", False) for c in meaningful):
        return "Process-confirmed"
    if any(c["rule"].get("process_level", False) for c in positive):
        return "Early"
    # Count readiness toward the same type; do not combine unrelated hypotheses.
    for kind in score.subscores:
        relevant = [c for c in meaningful if c["values"][kind] > 0]
        if (len({c["evidence"].signal_type for c in relevant}) >= cfg["emerging_min_signal_types"]
                and len({c["rule"]["category"] for c in relevant}) >= cfg["emerging_min_categories"]
                and len({c["evidence"].source_family for c in relevant}) >= cfg["emerging_min_source_families"]):
            return "Emerging"
    return "Early"


def assess(company: Company, raw: list[Evidence], as_of: date, config: dict) -> Assessment:
    events, lineage = deduplicate(eligible([e for e in raw if e.company_id == company.id], as_of), config)
    score = score_events(events, as_of, config)
    confidence = evidence_confidence(company, events, score, config)
    priority = round(score.transaction_propensity * confidence.evidence_confidence / 100, 1)
    thresholds = config["actions"]
    if priority >= thresholds["priority_1"] and confidence.evidence_confidence >= thresholds["priority_1_min_confidence"]:
        action = "Priority 1 — commission/update research"
    elif priority >= thresholds["priority_2"]:
        action = "Priority 2 — analyst review"
    elif priority >= thresholds["watchlist"]:
        action = "Watchlist"
    else:
        action = "No action"
    return Assessment(company, score, confidence, events, lineage, priority, action, signal_stage(score, as_of, config))


def rank_companies(companies: list[Company], raw: list[Evidence], as_of: date, config: dict) -> list[Assessment]:
    assessments = sorted([assess(c, raw, as_of, config) for c in companies], key=lambda a: (-a.priority, -a.score.transaction_propensity, a.company.id))
    for rank, assessment in enumerate(assessments, 1):
        assessment.rank = rank
    return assessments


def why_now(a: Assessment) -> str:
    kind = a.score.leading_type
    positive = sorted([c for c in a.score.contributions if c["values"][kind] > 0], key=lambda c: c["values"][kind], reverse=True)[:3]
    if positive:
        labels = "; ".join(f'{c["rule"]["label"].lower()} ({c["evidence"].event_date:%d %b})' for c in positive)
        rationale = f"Leading signals: {labels}."
    else:
        rationale = "No positive transaction catalyst survives the observed counter-signals."
    negatives = [c["rule"]["label"].lower() for c in a.score.contributions if c["values"][kind] < 0]
    counter = f" Counter-signal: {', '.join(negatives)}." if negatives else " No observed counter-signal; absence is not proof."
    if a.signal_stage == "Emerging":
        stage_text = "Emerging warning: independent readiness signals align. No public transaction process identified."
    elif a.signal_stage == "Process-confirmed":
        stage_text = "Process-confirmed: qualifying public evidence describes an explicit process or preparation; this does not confirm a deal or an ongoing process."
    elif any(c["rule"].get("process_level", False) for c in a.score.contributions):
        stage_text = "Early warning: process reporting is present but fails recency, strength or source-quality checks."
    else:
        stage_text = "Early warning: current evidence is insufficient to establish an active process."
    uncertainty = "; ".join(a.confidence.limitations) or "Timing and completion remain unverified"
    source_label = "family" if a.confidence.independent_sources == 1 else "families"
    return (f"{stage_text} {rationale}{counter} Evidence confidence is {a.confidence.label} "
            f"across {a.confidence.independent_sources} independent source {source_label}. {uncertainty.rstrip('.') }.")



def stage_description(a: Assessment | None, config: dict) -> str:
    """Shared stage definitions for the company drill-down and methodology."""
    cfg = config["stage_rules"]
    checks = (f"within {cfg['max_age_days']} days, strength ≥{cfg['minimum_strength']:g} "
              f"and source quality ≥{cfg['minimum_source_quality']:g}")
    process = ("Process-confirmed requires an explicit strategic review, sale report, IPO preparation "
               f"or refinancing mandate {checks}. It describes observed process evidence, not deal "
               "certainty or confirmation that the process is still active; counter-evidence remains visible.")
    emerging = (f"Emerging requires no process-level evidence and at least {cfg['emerging_min_signal_types']} "
                f"distinct positive signal types across {cfg['emerging_min_categories']} categories and "
                f"{cfg['emerging_min_source_families']} independent source families relevant to the same "
                f"transaction type, {checks}.")
    early = ("Early covers insufficient readiness evidence or process reporting that fails the checks. "
             "Negative and neutral events never advance the stage. Stage is not a score or probability.")
    if a is not None:
        return {"Early": early, "Emerging": emerging, "Process-confirmed": process}[a.signal_stage]
    return f"{process} {emerging} {early}"


def newest_impact(a: Assessment, as_of: date, config: dict) -> tuple[Evidence | None, float]:
    if not a.events:
        return None, 0
    newest = max(a.events, key=lambda e: (e.observed_date, e.id))
    without = score_events([e for e in a.events if e.id != newest.id], as_of, config)
    return newest, round(a.score.transaction_propensity - without.transaction_propensity, 1)

