from datetime import date, timedelta
import pytest
from src.ingestion import load_config, load_fixtures
from src.pipeline import assess, rank_companies, why_now


@pytest.fixture
def dataset():
    cfg = load_config()
    companies, events = load_fixtures()
    return cfg, {c.id: c for c in companies}, events, date.fromisoformat(cfg["as_of"])


@pytest.mark.parametrize("signal", ["strategic_review", "sale_reporting", "ipo_preparation", "refinancing_mandate"])
def test_explicit_process_evidence(dataset, signal):
    cfg, companies, events, stamp = dataset
    event = next(e for e in events if e.signal_type == signal)
    assert assess(companies[event.company_id], [event], stamp, cfg).signal_stage == "Process-confirmed"


def test_emerging_default_uses_readiness_only_and_honest_ranking(dataset):
    cfg, companies, events, stamp = dataset
    ranked = rank_companies(list(companies.values()), events, stamp, cfg)
    company = next(a for a in ranked if a.company.id == cfg["demo_default_company_id"])
    assert company.company.id == "northmere"
    assert company.signal_stage == "Emerging"
    assert not any(cfg["signals"][e.signal_type].get("process_level") for e in company.events)
    assert "adviser_engaged" not in {e.signal_type for e in company.events}
    assert company.action.startswith("Priority 2")
    assert "No public transaction process identified" in why_now(company)
    assert ranked[0].company.id != company.company.id
    assert [a.priority for a in ranked] == sorted([a.priority for a in ranked], reverse=True)


@pytest.mark.parametrize("company_id", ["elm", "fen", "solenne", "vesper"])
def test_early_includes_sparse_negative_and_uncorroborated_cases(dataset, company_id):
    cfg, companies, events, stamp = dataset
    assert assess(companies[company_id], events, stamp, cfg).signal_stage == "Early"


def test_negatives_cannot_escalate_or_erase_process_history(dataset):
    cfg, companies, events, stamp = dataset
    company = companies["northmere"]
    ready = [e for e in events if e.company_id == company.id]
    counter = next(e for e in events if e.signal_type == "sale_denied").model_copy(update={"company_id":company.id})
    assert assess(company,[counter],stamp,cfg).signal_stage == "Early"
    assert assess(company,ready+[counter],stamp,cfg).signal_stage == "Emerging"
    # A later denial reduces scores but stage describes observed process evidence.
    contradictory = assess(companies["morrow"],events,stamp,cfg)
    assert contradictory.signal_stage == "Process-confirmed"
    assert "Counter-signal:" in why_now(contradictory)


@pytest.mark.parametrize("update", [
    {"source_family":"one_origin"},
    {"strength":0.49},
    {"source_kind":"unverified"},
])
def test_emerging_requires_independence_strength_and_quality(dataset, update):
    cfg, companies, events, stamp = dataset
    ready = [e.model_copy(update=update) for e in events if e.company_id == "northmere"]
    assert assess(companies["northmere"],ready,stamp,cfg).signal_stage == "Early"


def test_recency_boundary_and_stale_process_not_mislabeled_emerging(dataset):
    cfg, companies, events, stamp = dataset
    ready = [e for e in events if e.company_id == "northmere"]
    boundary = stamp - timedelta(days=cfg["stage_rules"]["max_age_days"])
    at_boundary = [e.model_copy(update={"event_date":boundary}) for e in ready]
    stale = [e.model_copy(update={"event_date":boundary-timedelta(days=1)}) for e in ready]
    assert assess(companies["northmere"],at_boundary,stamp,cfg).signal_stage == "Emerging"
    assert assess(companies["northmere"],stale,stamp,cfg).signal_stage == "Early"
    process = next(e for e in events if e.signal_type == "strategic_review").model_copy(update={"company_id":"northmere","event_date":boundary-timedelta(days=1)})
    assert assess(companies["northmere"],ready+[process],stamp,cfg).signal_stage == "Early"


def test_three_categories_and_distinct_signal_types_required(dataset):
    cfg, companies, events, stamp = dataset
    ready = [e for e in events if e.company_id == "northmere"]
    two_categories = [e for e in ready if e.signal_type in {"sponsor_tenure","finance_hire","board_change"}]
    assert len({e.source_family for e in two_categories}) == 3
    assert assess(companies["northmere"],two_categories,stamp,cfg).signal_stage == "Early"
    repeated = [ready[0].model_copy(update={"id":f"copy-{i}","event_id":f"event-{i}","source_family":f"family-{i}"}) for i in range(3)]
    assert assess(companies["northmere"],repeated,stamp,cfg).signal_stage == "Early"


def test_high_score_and_adviser_alone_do_not_confirm_a_process(dataset):
    cfg, companies, events, stamp = dataset
    maturity = next(e for e in events if e.signal_type == "debt_maturity").model_copy(update={"company_id":"northmere","event_date":stamp,"source_kind":"registry","strength":1.0})
    a = assess(companies["northmere"],[maturity],stamp,cfg)
    assert a.score.transaction_propensity > 70
    assert a.signal_stage == "Early"
    adviser = maturity.model_copy(update={"signal_type":"adviser_engaged"})
    assert assess(companies["northmere"],[adviser],stamp,cfg).signal_stage == "Early"
