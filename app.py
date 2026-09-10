from datetime import date, timedelta
import hashlib
import json
import pandas as pd
import streamlit as st
from src.ingestion import ROOT, load_config, load_fixtures
from src.pipeline import rank_companies, why_now, newest_impact, stage_description
from src.scoring import TRANSACTIONS
from src.ui import esc, html, style

st.set_page_config(page_title="DealSignal Radar | Research priorities", page_icon="◉", layout="wide", initial_sidebar_state="collapsed")
style()
try:
    config = load_config()
    companies, raw_events = load_fixtures()
    as_of = date.fromisoformat(config["as_of"])
    assessments = rank_companies(companies, raw_events, as_of, config)
except (ValueError, OSError, KeyError) as error:
    st.error(f"Unable to load validated fixtures: {error}. Check data/ and config/signal_weights.json.")
    st.stop()
if not assessments:
    st.info("No companies loaded. Add validated company and evidence fixtures in data/.")
    st.stop()
by_id = {a.company.id: a for a in assessments}


def reset_queue_selection():
    # A dropdown change must not leave a different company's row highlighted.
    st.session_state.queue_revision = st.session_state.get("queue_revision", 0) + 1

default_company = config.get("demo_default_company_id")
if default_company not in by_id:
    default_company = assessments[0].company.id
st.session_state.setdefault("detail_company", default_company)
if st.session_state.detail_company not in by_id:
    st.session_state.detail_company = default_company

html(f'''<div class="brand"><div><div class="eyebrow">Private markets intelligence · Research planning</div><div class="brand-title">DealSignal Radar<span style="color:#087F74">.</span></div><div class="subtitle">Find the companies worth covering before the deal becomes the story.</div></div><div style="text-align:right"><span class="badge">OFFLINE DEMO</span><div class="small" style="margin-top:7px">Snapshot · {as_of:%d %b %Y}</div></div></div>
<div class="demo-note">Prototype/demo data — scores demonstrate methodology, not real-world transaction forecasts. All companies and evidence are fictional.</div>''')
period_start = as_of - timedelta(days=config["period_days"])
signals_period = sum(period_start < e.observed_date <= as_of for a in assessments for e in a.events)
priority_count = sum(a.action.startswith("Priority 1") for a in assessments)
kpis = [(str(len(companies)), "Demo scenarios", "Illustrative cases testing signal behaviours"), (str(priority_count).zfill(2), "High-priority companies", "Priority 1 · research commissioning queue"), (str(signals_period), "New signals / 30 days", "Unique events · syndicated copies removed"), (f"{sum(a.confidence.coverage for a in assessments)/len(assessments):.0f}%", "Average evidence coverage", "Source checks available · not confidence")]
html('<div class="kpis">' + ''.join(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>' for value,label,foot in kpis) + '</div>')
radar, explorer, methodology = st.tabs(["Research Priority Radar", "Evidence explorer", "Methodology & scale"])

with radar:
    columns = st.columns([1,1,1.45,1,1], gap="medium")
    country = columns[0].selectbox("Country", ["All countries"] + sorted({c.country for c in companies}))
    sector = columns[1].selectbox("Sector", ["All sectors"] + sorted({c.sector for c in companies}))
    transaction = columns[2].selectbox("Likely transaction", ["All transaction types", *TRANSACTIONS.values(), "No supported type"])
    min_propensity = columns[3].slider("Min. propensity index", 0, 100, 0, help="0–100 hypothesis-based signal-strength index; not a calibrated transaction probability.")
    min_confidence = columns[4].slider("Min. evidence confidence", 0, 100, 0, help="Reliability and completeness of the supporting evidence; separate from transaction propensity and not statistical model confidence.")
    filtered = [a for a in assessments if (country == "All countries" or a.company.country == country) and (sector == "All sectors" or a.company.sector == sector) and (transaction == "All transaction types" or TRANSACTIONS.get(a.score.likely_type, "No supported type") == transaction) and a.score.transaction_propensity >= min_propensity and a.confidence.evidence_confidence >= min_confidence]
    html(f'<div class="section-row"><div class="section-title">Research priority queue <span class="small">/ {len(filtered)} companies</span></div><div class="small">Prototype queue heuristic · select a row to investigate</div></div>')
    if filtered:
        rows = []
        for a in filtered:
            positive = sorted(a.score.contributions, key=lambda c: c["values"][a.score.leading_type], reverse=True)
            top = next((c["rule"]["label"] for c in positive if c["values"][a.score.leading_type] > 0), "No positive catalyst")
            newest = max((e.observed_date for e in a.events), default=None)
            rows.append({"Rank": a.rank, "Company": a.company.name, "Sector": {"Enterprise software": "Software", "Business services": "Services"}.get(a.company.sector, a.company.sector), "Country": {"United Kingdom": "UK", "United States": "US"}.get(a.company.country, a.company.country), "Propensity index": a.score.transaction_propensity, "Likely transaction": {"sale_buyout":"Sale / Buyout", "ipo":"IPO", "refinancing":"Refinancing"}.get(a.score.likely_type,"No supported type"), "Signal stage": a.signal_stage, "Evidence confidence": a.confidence.evidence_confidence, "Coverage": a.confidence.coverage, "Top signal": top, "Last signal": newest})
        signature = hashlib.sha256(json.dumps([country,sector,transaction,min_propensity,min_confidence]).encode()).hexdigest()[:12]
        queue_key = f"queue_{signature}_{st.session_state.get('queue_revision', 0)}"
        default_rows = [i for i, item in enumerate(filtered) if item.company.id == st.session_state.detail_company]
        table_event = st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=270, row_height=33, on_select="rerun", selection_mode="single-row", selection_default={"selection": {"rows": default_rows}}, key=queue_key, column_config={
            "Rank":st.column_config.NumberColumn("#",width=34),
            "Company":st.column_config.TextColumn(width=174),
            "Sector":st.column_config.TextColumn(width=100, help="Software = Enterprise software; Services = Business services."),
            "Country":st.column_config.TextColumn(width=68, help="UK = United Kingdom; US = United States."),
            "Propensity index":st.column_config.ProgressColumn("Propensity index",min_value=0,max_value=100,format="%.1f",width=128,help="0–100 hypothesis-based signal-strength index; not a calibrated transaction probability."),
            "Likely transaction":st.column_config.TextColumn(width=110),
            "Signal stage":st.column_config.TextColumn(width=134, help="Evidence maturity: Early, Emerging or Process-confirmed. Not a score or a guarantee of an active process."),
            "Evidence confidence":st.column_config.ProgressColumn("Evidence confidence",min_value=0,max_value=100,format="%.1f",color="#426486",width=147,help="Reliability and completeness of the supporting evidence; separate from transaction propensity and not statistical model confidence."),
            "Coverage":st.column_config.NumberColumn(format="%.0f%%",width=74),
            "Top signal":st.column_config.TextColumn(width=174),
            "Last signal":st.column_config.DateColumn(format="DD MMM YY",width=89)
        })
        if table_event.selection.rows:
            selected_index = table_event.selection.rows[0]
            marker = (queue_key, selected_index)
            if st.session_state.get("last_table_selection") != marker:
                st.session_state.detail_company = filtered[selected_index].company.id
                st.session_state.last_table_selection = marker
        if st.session_state.get("last_filter_signature") != signature and st.session_state.detail_company not in {a.company.id for a in filtered}:
            st.session_state.detail_company = filtered[0].company.id
        st.session_state.last_filter_signature = signature
        a = by_id[st.session_state.detail_company]
        newest, impact = newest_impact(a, as_of, config)
        html(f'''<div class="brief"><div class="brief-grid"><div><div class="eyebrow">Selected · #{a.rank:02d} · Signal stage: {a.signal_stage}</div><div class="company-title">{esc(a.company.name)}</div><div class="small">{esc(a.company.sector)} · {esc(a.company.country)}</div><div class="score-pair"><div><div class="score teal">{a.score.transaction_propensity:.1f}<span> /100</span></div><div class="mini-label">Propensity index</div></div><div><div class="score blue">{a.confidence.evidence_confidence:.1f}<span> /100</span></div><div class="mini-label">Evidence confidence · {a.confidence.label}</div></div></div></div><div><div class="eyebrow">Why now?</div><div class="why">{esc(why_now(a))}</div></div><div><span class="badge">{esc(a.action.split(' — ')[0])}</span><div class="why"><b>{esc(a.action.split(' — ')[-1].capitalize())}</b><br>{esc(TRANSACTIONS.get(a.score.likely_type,'No supported transaction type'))}</div><div class="mini-label">Prototype queue heuristic</div><div class="small" style="margin-top:8px">Newest event impact <b>{impact:+.1f} pts</b><br>Leave-one-event-out; not rank history.</div></div></div></div>''')
        st.caption("Propensity index = signal strength; Evidence confidence = evidence reliability. Both are 0–100 indices, not calibrated probabilities. Explore sources and counter-signals in Evidence explorer.")
    else:
        st.info("No companies match these filters. Lower a score threshold or select All countries / All sectors.")

with explorer:
    selected_id = st.selectbox("Investigate company", list(by_id), format_func=lambda cid: by_id[cid].company.name, key="detail_company", on_change=reset_queue_selection)
    a = by_id[selected_id]
    left, right = st.columns([1.6,1])
    with left:
        st.subheader(a.company.name)
        st.write(a.company.profile)
        st.caption(f"{a.company.country} · {a.company.sector} · {a.company.ownership} · Fictional scenario")
        st.markdown(f"**Signal stage: {a.signal_stage}** · {stage_description(a, config)}")
        st.markdown(f"**Coverage recommendation: {a.action}**")
        st.caption("Prototype queue heuristic; future commercial priority also requires client demand, coverage gaps/freshness and capacity.")
        st.write(why_now(a))
    with right:
        scores = st.columns(2)
        scores[0].metric("Propensity index", f"{a.score.transaction_propensity:.1f}/100")
        scores[1].metric(f"Evidence confidence · {a.confidence.label}", f"{a.confidence.evidence_confidence:.1f}/100")
        for kind, value in a.score.subscores.items():
            st.progress(value / 100, text=f"{TRANSACTIONS[kind]} · {value:.1f}/100")
    st.caption("Propensity index: 0–100 hypothesis-based signal strength, not a calibrated transaction probability. Evidence confidence: reliability and completeness, not statistical model confidence. The maximum type index is used.")
    signal_tab, calculation_tab, coverage_tab = st.tabs(["Signal & evidence timeline", "Score calculation", "Coverage & confidence"])
    with signal_tab:
        event_label = "event" if len(a.events) == 1 else "events"
        family_label = "family" if a.confidence.independent_sources == 1 else "families"
        st.markdown(f"**{len(a.events)} underlying {event_label} · {sum(len(v) for v in a.lineage.values())} source records · {a.confidence.independent_sources} independent source {family_label}**")
        category = st.selectbox("Signal category", ["All categories"] + sorted({c["rule"]["category"] for c in a.score.contributions}), key="category_filter")
        shown = [c for c in a.score.contributions if category == "All categories" or c["rule"]["category"] == category]
        for i,c in enumerate(shown):
            e = c["evidence"]
            contribution = c["values"][a.score.leading_type]
            label = "Positive" if c["rule"]["direction"] > 0 and c["rule"]["weight"] else "Counter-signal" if c["rule"]["direction"] < 0 else "Context only"
            with st.expander(f"{e.event_date:%d %b %Y} · {c['rule']['label']} · {label} · {contribution:+.1f} raw points", expanded=i == 0):
                st.caption(f"{e.id} → {e.event_id} → {e.source_name} · ILLUSTRATIVE")
                st.write(e.supporting_evidence)
                st.markdown(f"**Source:** {e.source_name} · **Source family:** `{e.source_family}`")
                st.caption(f"Event: {e.event_date} · Published/filed: {e.published_date} · First observed: {e.observed_date}")
                st.caption(f"Category: {c['rule']['category']} · Strength: {e.strength:.2f} · Quality multiplier: {c['quality']:.2f} · Recency multiplier: {c['recency']:.3f}")
                if e.source_url:
                    st.link_button("Open public source", e.source_url)
                else:
                    st.caption("No public URL — this is an illustrative evidence record, not a real source.")
                copies = a.lineage[e.id]
                if len(copies) > 1:
                    st.info(f"{len(copies)} records resolve to one event. Syndication does not increase the score or independent-source count.")
                    st.dataframe(pd.DataFrame([{"Record":copy.id,"Source":copy.source_name,"Family":copy.source_family,"Published":copy.published_date,"URL":copy.source_url or "Illustrative — no URL"} for copy in copies]), hide_index=True, width="stretch")
        st.download_button("Download evidence audit JSON", json.dumps({"as_of":str(as_of),"config_version":config["version"],"company":a.company.model_dump(mode="json"),"evidence_records":[e.model_dump(mode="json") for group in a.lineage.values() for e in group]},indent=2),file_name=f"{a.company.id}-evidence.json",mime="application/json")
    with calculation_tab:
        st.markdown("**Each event:** weight × direction × strength × type relevance × source quality × recency.")
        st.code("recency = 2 ** (-age_days / 180)\ntype_index = 100 × (1 - exp(-max(raw_points, 0) / 65))\npropensity_index = max(sale_index, ipo_index, refinancing_index)\nprototype_queue_heuristic = propensity_index × evidence_confidence / 100",language="text")
        st.caption("Raw points are additive before normalization. A +10 raw-point signal is not a +10 index-point change. See config/signal_weights.json for every assumption.")
        st.dataframe(pd.DataFrame([{"Evidence ID":c["evidence"].id,"Signal":c["rule"]["label"],"Base weight":c["rule"]["weight"],"Direction":c["rule"]["direction"],"Strength":c["evidence"].strength,"Source quality":c["quality"],"Recency":round(c["recency"],3),**{TRANSACTIONS[k]:round(v,2) for k,v in c["values"].items()}} for c in a.score.contributions]),hide_index=True,width="stretch")
        if a.score.interactions:
            st.markdown("**Complementary signal bonuses** — different events and independent source families required.")
            st.dataframe(pd.DataFrame(a.score.interactions),hide_index=True,width="stretch")
        else:
            st.caption("No complementary-signal bonus applies.")
        newest, impact = newest_impact(a, as_of, config)
        if newest:
            st.info(f"What changed? Newest event {newest.id}, observed {newest.observed_date}: {config['signals'][newest.signal_type]['label']}. Removing this event and its interaction bonuses changes overall propensity by {impact:+.1f} points. This is a counterfactual contribution, not a recorded historical rank movement.")
    with coverage_tab:
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Source availability checks**")
            for name in ["registry","company","ownership","financial","news"]:
                st.write(f"{'✓' if a.company.coverage.get(name,False) else '—'} {name.title()}: {'available' if a.company.coverage.get(name,False) else 'missing / not checked'}")
            st.caption("Availability flags are illustrative analyst inputs. Available does not mean a source contains transaction evidence. Missing evidence is not evidence of no transaction.")
        with cols[1]:
            for name,value in a.confidence.factors.items():
                st.progress(value,text=f"{name.capitalize()} · {value:.0%} · weight {config['confidence']['weights'][name]:.0%}")
        st.write("; ".join(a.confidence.limitations) or "All expected source classes checked. Timing, extraction accuracy and deal completion still require validation.")
        st.caption("Evidence confidence is a heuristic evidence index. One independent source caps confidence at 45; two cap it at 68. Duplicated events contribute one representative source. High ≥75, Medium ≥50, otherwise Low.")

with methodology:
    st.subheader("A research queue, with an evidence trail")
    st.write("Target: a material sale/acquisition/buyout, IPO, or refinancing/recapitalisation announced in the next 365 days. Ordinary funding rounds are input signals. An already announced qualifying deal leaves the at-risk universe; closing it later is not a new prediction win.")
    st.markdown("**Public sources → Change detection + entity resolution → Structured event extraction → Signal store → Transaction propensity → Evidence-quality gate → Commercial research priority → Analyst feedback**")
    st.caption("Commercial research priority — future: client demand + coverage gap/freshness + capacity. These inputs and a standalone production quality gate are not implemented. Deduplication and evidence lineage remain part of ingestion.")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("**Where AI earns its place**")
        st.write("Use LLMs to turn unstructured public evidence into structured events; use deterministic/ML systems to aggregate, rank, calibrate and monitor those events.")
        st.write("This demo uses normalized fixtures, validated schemas, rule weights, smooth recency decay and deterministic explanations. The optional LLM adapter is an integration seam with schema validation, exact-quote checks and graceful fallback; no live model is connected.")
        st.markdown("**Propensity index ≠ Evidence confidence**")
        st.write("Propensity asks how strongly observed signals indicate a transaction. Confidence asks how reliable and complete those observations are. A low score with high confidence can justify no action; a high score with low confidence calls for corroboration.")
        st.markdown("**Forecasting versus commercial action**")
        st.write("Forecasting asks which private companies show evidence of entering a material transaction within approximately 12 months. Commercial action asks where Third Bridge should deploy scarce research capacity given transaction propensity and evidence quality.")
        st.write("This POC uses propensity index × evidence confidence / 100 as a transparent prototype queue heuristic. In production, transaction propensity would first pass an evidence-quality gate, then combine with expected client demand, existing coverage gaps/freshness and research capacity to determine commercial priority. These commercial inputs are not implemented.")
        st.caption("Prototype hypotheses: Priority 1 ≥55 and evidence confidence ≥75; Priority 2 ≥30; Watchlist ≥12; otherwise No action.")
    with col2:
        st.markdown("**Validation path: 14 demo scenarios → 100-company shadow pilot → 100k universe**")
        st.write("14 fictional scenarios validate system behaviour and UI. A future 100-company point-in-time shadow pilot validates data coverage and workflow. Only then scale ingestion and scoring toward a 100,000-company universe; the pilot has not been completed.")
        st.write("Use source-specific adapters and scheduled delta updates; hash and cache documents, resolve entities, and queue batches. Parse structured sources cheaply first. Send only new, high-value unstructured documents to a small model, escalating difficult cases to a larger model or analyst. Keep immutable evidence lineage and point-in-time features.")
        st.write("Train time-aware propensity models on historical outcomes, calibrate held-out probabilities, and monitor coverage, drift, source outages and analyst overrides. Keep evidence confidence separate from predictive probability calibration.")
        st.markdown("**Cost drivers, not invented budgets**")
        st.write("New document volume × extraction share × token length × model routing drives inference cost. Company count alone is insufficient. Also budget for permitted data access, refresh frequency, storage, entity resolution and human review.")
        st.markdown("**Validate before trusting**")
        st.write("Backtest point-in-time snapshots with mature 365-day labels. Measure Precision@K, Lift@K, Recall@K, PR-AUC, calibration/Brier score, lead time and source coverage. Then measure whether commissioned research meets later client demand and whether analysts override the queue. No predictive results are claimed here.")
    st.markdown("**Signal stage: earlier warning versus explicit process evidence**")
    st.write(stage_description(None, config))
    st.write("Direct process signals are likely to maximise precision but may arrive too late to create useful research lead time. The key validation question is whether combinations of earlier, weaker signals create sufficient lift while preserving actionable lead time. This is a hypothesis to test, not a measured POC result.")
    with st.expander("Signal taxonomy and editable assumptions"):
        st.dataframe(pd.DataFrame([{"Signal":r["label"],"Category":r["category"],"Weight":r["weight"],"Direction":r["direction"]} for r in config["signals"].values()]),hide_index=True,width="stretch")
        st.caption("Direct process evidence is weighted above indirect readiness, operational momentum or sector context. Negative indicators are transaction-specific. All weights are unvalidated hypotheses.")
    st.warning("Prototype limitations: fictional fixtures; no live ingestion; no learned probabilities; simplified entity/event deduplication; manually assigned coverage; no demonstrated forecasting skill. Public-data licensing, geographical coverage, historical labels and signal predictive power must be validated first.")
    st.caption("Assignment alignment: the source PDF is design-led with a three-slide cap. This 14-company implementation is supporting material; the next pilot is 100 companies before any 100k rollout. See README.md, docs/EVALUATION.md and docs/SLIDE_GUIDE.md.")



