from datetime import date, timedelta
import json
import pytest
from pydantic import ValidationError
from src.ingestion import load_config, load_fixtures, deduplicate, eligible
from src.pipeline import assess, rank_companies, newest_impact
from src.scoring import recency_decay, score_events
from src.extractors.llm import LLMExtractor
from src.extractors.rules import RulesExtractor


@pytest.fixture
def fixture():
    config = load_config()
    companies, events = load_fixtures()
    return config, companies, events, date.fromisoformat(config["as_of"])


def test_recency_continuous_half_life_and_monotonic():
    assert recency_decay(0,180) == 1
    assert recency_decay(180,180) == pytest.approx(.5)
    assert recency_decay(360,180) == pytest.approx(.25)
    assert recency_decay(31,180) < recency_decay(30,180)
    with pytest.raises(ValueError): recency_decay(-1,180)
    with pytest.raises(ValueError): recency_decay(1,0)


def test_exact_single_signal_formula(fixture):
    import math
    config, companies, events, stamp = fixture
    event = next(e for e in events if e.signal_type == "ipo_preparation").model_copy(update={"event_date":stamp,"strength":1.0,"source_kind":"registry"})
    score = score_events([event],stamp,config)
    assert score.subscores["ipo"] == round(100 * (1-math.exp(-140/65)),1)
    assert score.likely_type == "ipo"
    assert score.subscores["refinancing"] == 0


def test_syndicated_copies_do_not_raise_propensity_or_confidence(fixture):
    cfg, companies, events, stamp = fixture
    company = next(c for c in companies if c.id == "vesper")
    originals = [e for e in events if e.company_id == "vesper" and "copy" not in e.id]
    first, repeated = assess(company,originals,stamp,cfg), assess(company,events,stamp,cfg)
    assert first.score == repeated.score
    assert first.confidence == repeated.confidence
    assert repeated.confidence.evidence_confidence <= 45
    assert len(repeated.events) == 1
    assert len(next(iter(repeated.lineage.values()))) == 4


def test_exact_text_duplicate_with_different_event_id(fixture):
    cfg,_,events,_ = fixture
    original = events[0]
    copy = original.model_copy(update={"id":"copy","event_id":"other","source_family":"other"})
    deduped, lineage = deduplicate([original,copy],cfg)
    assert len(deduped) == 1
    assert len(next(iter(lineage.values()))) == 2


def test_dedupe_is_company_scoped_and_distinct_signals_remain(fixture):
    cfg,_,events,_ = fixture
    original = events[0]
    other_company = original.model_copy(update={"id":"different-company","company_id":"other"})
    other_signal = original.model_copy(update={"id":"different-signal","event_id":"separate-event","signal_type":"growth"})
    assert len(deduplicate([original,other_company,other_signal],cfg)[0]) == 3


def test_future_publication_or_observation_cannot_leak(fixture):
    _,_,events,stamp = fixture
    event = events[0]
    assert eligible([event.model_copy(update={"observed_date":stamp+timedelta(days=1)})],stamp) == []
    assert eligible([event.model_copy(update={"published_date":stamp+timedelta(days=1)})],stamp) == []


def test_negative_evidence_lowers_type_and_agreement(fixture):
    cfg,companies,events,stamp = fixture
    company = next(c for c in companies if c.id == "morrow")
    all_evidence = assess(company,events,stamp,cfg)
    without_denial = assess(company,[e for e in events if e.signal_type != "sale_denied"],stamp,cfg)
    assert all_evidence.score.subscores["sale_buyout"] < without_denial.score.subscores["sale_buyout"]
    assert all_evidence.confidence.factors["agreement"] < without_denial.confidence.factors["agreement"]
    assert any("Contradictory" in x for x in all_evidence.confidence.limitations)


@pytest.mark.parametrize("company_id,kind", [("alderwick","sale_buyout"),("luma","ipo"),("stonehaven","refinancing"),("solenne",None)])
def test_transaction_type_classification(fixture,company_id,kind):
    cfg,companies,events,stamp = fixture
    a = assess(next(c for c in companies if c.id == company_id),events,stamp,cfg)
    assert a.score.likely_type == kind


def test_high_propensity_low_confidence_and_low_propensity_high_confidence(fixture):
    cfg,companies,events,stamp = fixture
    results = {a.company.id:a for a in rank_companies(companies,events,stamp,cfg)}
    assert results["vesper"].score.transaction_propensity > 65
    assert results["vesper"].confidence.label == "Low"
    assert not results["vesper"].action.startswith("Priority 1")
    assert results["solenne"].score.transaction_propensity < 10
    assert results["solenne"].confidence.label == "High"
    assert results["solenne"].action == "No action"


def test_missing_coverage_and_source_quality_reduce_confidence(fixture):
    cfg,companies,events,stamp = fixture
    company = companies[0]
    good = assess(company,events,stamp,cfg)
    sparse = assess(company.model_copy(update={"coverage":{k:False for k in company.coverage}}),events,stamp,cfg)
    poor = assess(company,[e.model_copy(update={"source_kind":"unverified"}) for e in events],stamp,cfg)
    assert sparse.confidence.evidence_confidence < good.confidence.evidence_confidence
    assert poor.confidence.evidence_confidence < good.confidence.evidence_confidence


def test_interaction_requires_independence(fixture):
    cfg,_,events,stamp = fixture
    pair = [next(e for e in events if e.company_id == "alderwick" and e.signal_type == signal) for signal in ["strategic_review","sponsor_tenure"]]
    assert len(score_events(pair,stamp,cfg).interactions) == 1
    same_family = [e.model_copy(update={"source_family":"same"}) for e in pair]
    assert score_events(same_family,stamp,cfg).interactions == []


def test_new_signal_impact_recomputes_interactions(fixture):
    cfg,companies,events,stamp = fixture
    a = assess(next(c for c in companies if c.id == "luma"),events,stamp,cfg)
    event,delta = newest_impact(a,stamp,cfg)
    assert event.signal_type == "ipo_preparation"
    remaining = score_events([e for e in a.events if e.id != event.id],stamp,cfg)
    assert not remaining.interactions
    assert delta == round(a.score.transaction_propensity - remaining.transaction_propensity,1)


def test_empty_evidence_and_zero_scores(fixture):
    cfg,companies,_,stamp = fixture
    a = assess(companies[0],[],stamp,cfg)
    assert a.score.transaction_propensity == a.confidence.evidence_confidence == 0
    assert a.score.likely_type is None
    assert a.action == "No action"


def test_fixture_integrity_and_score_ranges(fixture):
    cfg,companies,events,stamp = fixture
    assert len(companies) == 14
    assert all(e.illustrative and e.source_url is None for e in events)
    results = rank_companies(companies,events,stamp,cfg)
    assert all(0 <= a.score.transaction_propensity <= 100 and 0 <= a.confidence.evidence_confidence <= 100 for a in results)
    assert [a.priority for a in results] == sorted([a.priority for a in results],reverse=True)
    with pytest.raises(ValidationError):
        type(events[0]).model_validate({**events[0].model_dump(),"illustrative":False,"source_url":None})


def test_llm_missing_and_failed_transport_fall_back():
    assert LLMExtractor().extract("text").mode == "fallback"
    def failure(prompt,schema):
        raise TimeoutError("credential-containing failure")
    result = LLMExtractor(failure).extract("text")
    assert result.events == [] and "credential" not in result.warning


def test_llm_schema_quote_and_taxonomy_validation():
    event = dict(company="Fictional",event_date="2026-09-01",signal_type="strategic_review",transaction_type_relevance=["sale_buyout"],direction=1,strength=.8,entities=["Fictional"],supporting_evidence="The board is reviewing a sale.",reason="Explicit intent",uncertainty="No timetable")
    valid = json.dumps([event])
    assert RulesExtractor().extract(valid).mode == "normalized_fixture"
    assert LLMExtractor(lambda p,s:valid).extract(event["supporting_evidence"]).mode == "llm"
    assert LLMExtractor(lambda p,s:valid).extract("Unrelated text").mode == "fallback"
    for update in [{"strength":2},{"transaction_probability":.9},{"signal_type":"invented"},{"direction":-1}]:
        assert LLMExtractor(lambda p,s:json.dumps([{**event,**update}])).extract(event["supporting_evidence"]).mode == "fallback"
