# DealSignal Radar

A small, offline-first research-prioritisation proof of concept for Third Bridge's **Senior Analyst, AI Implementation** take-home assignment.

**Prototype/demo data — scores demonstrate methodology, not real-world transaction forecasts.** Every company, profile, source name and evidence passage in the shipped dataset is fictional. No fabricated public URLs are used. A high score means strong signals under explicitly hypothetical rules, not a 97% chance of a deal.

## Start the demo

Python 3.11 or later; no database, API key or external service required.

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501. From this checkout, the tested virtual environment is also ready:

```powershell
.\.venv\Scripts\python -m streamlit run app.py
.\.venv\Scripts\python -m pytest -q
```

For a fresh isolated environment, run `python -m venv .venv`, activate it (`.\.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS/Linux), then use the first commands. Dependencies are pinned to versions tested here. `pytest` is included so verification needs no extra install. PDF-reading and browser-development tooling are not runtime dependencies.

## The business decision

Third Bridge can commission expert interviews and update company briefs before transaction-driven client demand arrives. The product turns attributable public events into a ranked **coverage queue**. Analysts investigate the evidence, challenge the hypothesis and choose what research to commission. This is research decision support, not an autonomous investment recommendation.

The root [assignment PDF](TB_AI_Team_External_Candidate_Take_Home_Assignment.pdf) asks for a design-led concept, a 100-company exercise and a path to approximately 100,000 companies. It caps the principal submission at **three slides**. Following this implementation brief, this repository deliberately demonstrates 14 contrasting scenarios, with the 100-company pilot as the next validation step. The application is supporting material; [the three-slide narrative guide](docs/SLIDE_GUIDE.md) explains how to use it without exceeding that cap.

### Two related decisions

**Forecasting question:** Which private companies show evidence of entering a material transaction within the next ~12 months?

**Commercial action question:** Given transaction propensity and evidence quality, where should Third Bridge deploy scarce research capacity?

These are related but not identical. Direct process signals are likely to maximise precision but may arrive too late to create useful research lead time. The key validation question is whether combinations of earlier, weaker signals create sufficient lift while preserving actionable lead time. This is an important hypothesis illustrated by the POC, not an empirical finding.

**Validation path: 14 demo scenarios → 100-company shadow pilot → 100k universe.** The 14 fictional behaviour/test scenarios exercise UI and system logic. The future 100-company point-in-time shadow pilot tests source coverage and analyst workflow before scaling. The pilot has not been completed. The first KPI is intentionally **Demo scenarios**, not a claim of live monitoring coverage.

## What this slice demonstrates

- A presentation-ready Research Priority Radar, country/sector/type/score filters, selectable rows and company-specific explanations.
- Separate transaction-propensity and evidence-confidence indices, transaction-type sub-scores and research actions.
- An auditable chain: **company → score contribution → signal → evidence ID → canonical event → source metadata**.
- Publication, event and first-observed dates, source quality, smooth decay, counter-signals and retained syndication lineage.
- A deterministic pipeline that runs offline, plus a provider-neutral, schema-validated LLM extraction adapter.
- Meaningful tests and an evaluation utility for future supplied labels; no manufactured backtest performance.

It does not deliver live monitoring, actual company forecasts, scraping, production entity resolution, a trained model, authentication, a database, a production LLM integration or a slide deck. No scheduled service is implied by the static snapshot. The screen shows **10 September 2026**, independent of your computer's current date, so the interview is reproducible.

## Product tour

The initial table uses **propensity index × evidence confidence / 100**, a prototype queue heuristic, with company-ID tie-breaking for reproducibility. Rank is across the full universe and remains unchanged when filtered. The default detail is **Northmere Components**, an Emerging case; this selection does not alter its actual queue rank. Select any row to update its compact brief. Switch to **Evidence explorer** to inspect or select a company, expand the timeline, inspect score calculations, and download the source audit JSON. **Methodology & scale** makes assumptions visible in the product.

Useful contrasting scenarios:

| Company | Deliberate scenario | Research implication |
|---|---|---|
| Northmere Components | Emerging sponsor-backed readiness; no public transaction process identified | Default example: Priority 2 analyst review; honest rank #5 |
| Alderwick Systems | Strong exit signals, broad corroboration | Priority 1: commission/update research |
| LumaForge Analytics | Listing preparation and independent finance hire | IPO hypothesis; inspect event lineage |
| Stonehaven Packaging | Debt maturity plus refinancing mandate | Credit-oriented research coverage |
| Vesper Harbor Health | Strong single-origin sale claim, three syndicated copies | Elevated propensity, Low confidence; corroborate first |
| Morrowfield Digital | Sale report followed by explicit company denial | Counter-signal reduces propensity; inspect disagreement |
| Solenne Field Services | Broad coverage, no surviving catalyst | Low propensity, High confidence; no current action |
| Elmridge Materials / Fenwick Reach | Sparse, stale evidence | Low scores cannot establish absence of a deal |

The newest-event indicator is a **leave-one-event-out change in propensity**, recomputed including interactions. It is not a historical rank-change claim. The count of new signals uses first-observed dates in `(as_of - 30 days, as_of]`, after deduplication. Coverage KPIs measure five expected source classes, not predictive confidence.

## Architecture

```text
app.py                         Streamlit interface, selection, evidence drill-down
config/signal_weights.json     All scoring/confidence/action assumptions
src/models.py                  Validated company and evidence contracts
src/ingestion.py               CSV/JSON loader, eligibility, event deduplication
src/scoring.py                 Transaction-specific weights, decay, interactions
src/confidence.py              Independent evidence-confidence calculation
src/pipeline.py                Signal stage, queue actions, ranking, why-now explanations
src/extractors/                Normalized input + optional LLM extraction seam
src/evaluation.py              Metrics for supplied mature historical labels
src/ui.py                      Restrained visual styling
scripts/generate_fixtures.py   Reproducible fictional scenarios; no network
tests/                        Engine, extraction, evaluation and UI checks
docs/                         Evaluation, scaling, source policy, slide guidance
```

### Why this architecture?

**“Use LLMs to turn unstructured public evidence into structured events; use deterministic/ML systems to aggregate, rank, calibrate and monitor those events.”**

Language models help interpret inconsistent language, named entities, negation and event descriptions. They should not invent a final 12-month probability. Separating extraction from scoring gives analysts a traceable explanation, permits independent evaluation of extraction quality, and makes a future model replaceable without rewriting the source pipeline or UI. JSON configuration uses the standard library instead of adding a YAML dependency. Simple files, pandas and Pydantic are sufficient for the implementation slice; no agent framework or scikit-learn dependency is needed.

### AI versus deterministic boundaries

The running app consumes already-normalized `Evidence` records and validates them with Pydantic. `RulesExtractor` validates normalized candidate-event JSON; it does **not** claim to understand arbitrary prose. `LLMExtractor` is an optional integration seam accepting a caller-supplied `transport(prompt, schema)` callable. It requests structured output, validates the taxonomy/direction/strength, rejects added probability fields and checks that the supporting quote exists in the source text. It never writes into the signal store.

No provider or API key is configured, auto-detected, or used by the UI. Missing transport, network exceptions, malformed responses and unattributable text return an empty candidate result and a safe warning; the existing fixture pipeline remains usable. See [the extraction contract](docs/EXTRACTION.md) for a sample and the remaining review gates. A production transport needs authentication, bounded timeouts/retries, approved data handling and provider-specific structured-output setup.

## Transaction definition and scoring

The primary target is the **first public announcement** of a material sale/acquisition/control buyout, IPO, or refinancing/recapitalisation in the next 365 days. Ordinary equity fundraising, a finance hire or a charge filing are inputs, not automatic positive outcome labels. A charge may record financing already completed; it is deliberately a weak signal requiring interpretation. Already-announced qualifying deals leave the at-risk universe; later closing must not count as a forecasting success. Preparatory reviews and filings remain signals until the chosen qualifying event boundary. Materiality, IPO event boundary and recapitalisation thresholds need agreement before labels are collected.

All assumptions live in [config/signal_weights.json](config/signal_weights.json), including the explicit scoring date, source multipliers, target relevance, normalization scale and confidence/action thresholds. Direct intent has much larger weights than sector context or growth. Direction is transaction-specific: a sale denial need not contradict refinancing.

For each eligible, deduplicated event and transaction type:

```text
raw contribution = base weight × direction × strength × type relevance
                   × source quality × recency
recency = 2 ** (-days since event / half_life_days)
type index = 100 × (1 - exp(-max(sum(contributions) + bonuses, 0) / scale))
transaction_propensity = max(sale/buyout index, IPO index, refinancing index)
```

The current half-life is 180 days and scale is 65. This saturating transformation maps nonnegative evidence strength to 0–100; it is **not fitted or calibrated**. The sub-scores do not sum to 100 and are not mutually exclusive probabilities. If the strongest sub-score is below 15, the UI says “No supported type” instead of assigning a spurious transaction. No base-rate intercept is assumed; zero means no positive score under these rules, not zero real-world risk.

Three small interactions represent complementary exit-readiness/direct-intent, IPO/finance-hire, and maturity/refinancing signals. They require different canonical events and source families, apply once per configured pair and decay by the weaker supporting evidence. All underlying evidence IDs are displayed. Raw contributions are additive before normalization; they must not be read as index-point increments.

### Signal stage: evidence maturity, not another score

The assessment carries `signal_stage: Literal["Early", "Emerging", "Process-confirmed"]`. It reuses eligible, deduplicated scoring contributions and existing source quality; it does not change the scoring formula, weights, confidence or ranking.

- **Process-confirmed:** at least one explicit strategic review, sale process report, public IPO preparation or refinancing mandate, within 180 days, strength ≥0.5 and source quality ≥0.7. These four taxonomy entries carry `process_level: true`. An ambiguous adviser engagement or debt maturity alone does not meet this definition.
- **Emerging:** no positive process-level evidence in the available records, and at least three distinct positive signal types across three categories and three independent source families, all relevant to the same transaction type and meeting the same age/strength/quality checks. This is a simple breadth-and-independence rule, not a propensity cutoff.
- **Early:** all other cases, including sparse readiness or weak/stale process reporting. A process record that fails the checks conservatively prevents the “no public process identified” Emerging claim.

Negative and zero-weight/context-only events cannot advance the stage. Stage describes observed process evidence, **not confirmation that a process is currently active or a deal will happen**. A subsequent denial/postponement remains visible and reduces the appropriate propensity contribution without erasing the earlier process observation. Thresholds in `stage_rules` are transparent hypotheses; emerging lead time must be validated historically.

**Default scenario:** Northmere Components has a mature sponsor holding, finance leadership change, board changes, a new security filing, operational expansion and sector consolidation. These are six recent signal types, five categories and five source families, with no explicit process signal and no adviser mandate. Existing weights yield **54.5/100 Propensity index**, **91.5/100 Evidence confidence**, **rank #5**, and **Priority 2 — analyst review**. The score is deliberately not inflated to a target screenshot range. No scoring weight or interaction bonus was changed for this example.

UI labels are **Propensity index** and **Evidence confidence**, both 0–100 indices, never percentage probabilities. Only source-availability coverage uses a percentage. Evidence confidence means reliability and completeness of supporting evidence, not statistical model confidence.

### Evidence confidence is separate

Confidence uses a weighted sum of six 0–1 factors:

| Factor | Weight | Implementation |
|---|---:|---|
| Source quality | 25% | Average best quality per independent originating family |
| Independence | 20% | Independent families / 4, capped at one |
| Recency | 15% | Average freshest event decay per family |
| Signal-category breadth | 10% | Unique categories / 4, capped at one |
| Agreement | 10% | Absolute positive-minus-negative raw evidence / total absolute evidence for leading type |
| Data completeness | 20% | Available registry, company, ownership, financial and news source checks / 5 |

No eligible events gives confidence zero. One source family caps confidence at 45; two cap it at 68. Labels are High ≥75, Medium ≥50, Low otherwise. Several neutral observations can support confidence that public coverage was reviewed even when no catalyst exists. Agreement is one for no directional evidence, but source, recency and completeness constraints still apply. These are engineering hypotheses, not measured extraction accuracy or probability uncertainty bounds.

Duplicates merge on company + canonical event ID or company + signal type + exact normalized evidence-text hash. The representative prefers original reporting, then credibility, then earliest publication, retaining every duplicate for audit. One underlying event contributes one vote; republication does not reset the event date. Source family represents editorial ownership/origin, not a count of URLs. Distinct signals in one document may survive, but a prolific publisher cannot alone raise independence. Semantic paraphrases and shared unnamed sources still require a production resolver.

### From ranking to action

```text
prototype_queue_heuristic = propensity_index × evidence_confidence / 100
Priority 1 — commission/update research: priority ≥55 AND confidence ≥75
Priority 2 — analyst review:             priority ≥30
Watchlist:                              priority ≥12
No action:                              otherwise
```

This multiplication is the **prototype queue heuristic**, not the mature commercial prioritisation function, expected monetary value or a joint probability. Production concept: **Transaction propensity → Evidence-quality gate → Commercial research priority**. Future commercial priority additionally considers expected client demand, existing Third Bridge coverage gaps/research freshness and available analyst/research capacity. These inputs and a standalone production quality gate are not implemented, and no values are fabricated. The displayed action thresholds remain prototype hypotheses. Sparse high-propensity cases need corroboration; an analyst may still override the queue, with a recorded reason.

## Data and source policy

No factual private-company data was collected for this build. [data/README.md](data/README.md) describes the fictional fixture contract and future public-source classes. Real records must include a public URL and publication/observed/event dates; illustrative records must not include invented URLs. Do not load confidential client holdings, communications or internal relationship data as external evidence. Public visibility alone does not grant permission to scrape, store or republish content: validate licensing/terms and retention before adapters are enabled.

To expand to a 100-company fixture, add company rows with stable IDs to `data/companies.csv` and attributable evidence objects to `data/evidence.json`; no scoring or UI changes are required for the same illustrative schema. Both files are loaded by paths relative to the application, not the shell directory. Unknown companies/signals, duplicate record IDs, malformed dates and invalid strengths fail clearly. `python scripts/generate_fixtures.py` intentionally resets the two fixture files to the shipped fictional scenarios; do not run it over collected data you wish to keep.

## Evaluation and production evolution

[docs/EVALUATION.md](docs/EVALUATION.md) specifies point-in-time label construction, rolling temporal holdouts, censoring, leakage controls, ranking metrics, calibration, lead time and commercial evaluation. A ready-to-use utility accepts your own mature labelled CSV:

```powershell
python -m src.evaluation path/to/labelled_snapshot.csv --k 20
```

Add `--calibrated` only when `score` contains independently calibrated probabilities; this enables Brier score. There are **no backtest results** in this repository. Toy arrays in unit tests verify arithmetic and are not evidence of predictive performance.

[docs/SCALE.md](docs/SCALE.md) describes source-specific delta ingestion, document hashing/caching, batch queues, entity resolution, selective small/large-model routing, point-in-time event/feature stores, calibrated models, monitoring and analyst feedback. Major variable cost depends on **new document volume and extraction policy**, not company count alone. No fabricated dollar estimate is offered.

## What I would validate first

1. **Signal predictive power and useful lead time.** Does direct reporting arrive early enough to change research decisions, or merely repeat demand that has already arrived? Test incremental lift over source coverage, sector and ownership-age baselines.
2. **Historical labels and availability timestamps.** Can we obtain lawfully usable transaction outcomes and historical versions of evidence, including failures and quiet companies? Without this, calibrated probability claims are unjustified.
3. **Geographical source coverage.** Registry timeliness, language, private disclosure and press attention vary; distinguish low evidence from low propensity. Audit results by region, sector, size and ownership.
4. **Entity and event resolution.** Subsidiaries, renamed firms, sponsor entities and syndicated articles can create false joins or inflated evidence. Review a stratified gold set before expanding.
5. **Public-data licensing/ToS.** Confirm retrieval, caching, retention, excerpt use, model-processing rights and source-specific rate limits. Do not bypass access controls.
6. **Calibration and queue usefulness.** Estimate reliability only on untouched temporal holdouts; check whether analysts would actually commission valuable research from the top K and measure later client consumption.

Next: agree target/materiality and research capacity; validate a 100-company pilot with labelled source audits; establish point-in-time history and simple baselines; run shadow queues with analysts; expand coverage only after quality, cost and commercial gates hold.

## Tests, screenshot and interview material

```powershell
pytest
```

Tests cover stage eligibility, independence, negative evidence, default selection and terminology, plus decay, score math, source deduplication, negative evidence, confidence, classification, interactions, date eligibility, schema/provenance validation, graceful extraction fallback, evaluation and Streamlit controls.

Open the app at 1440×900, browser zoom 100%, default filters and Northmere Components selected automatically. The main screenshot is [output/playwright/dealsignal-radar-1440x900.png](output/playwright/dealsignal-radar-1440x900.png). [DEMO.md](DEMO.md) is the two-minute speaking script; [docs/SLIDE_GUIDE.md](docs/SLIDE_GUIDE.md) is the three-slide narrative.

UI implementation references: Streamlit's official [dataframe selection API](https://docs.streamlit.io/develop/api-reference/data/st.dataframe) and [progress-column API](https://docs.streamlit.io/develop/api-reference/data/st.column_config/st.column_config.progresscolumn). These are software references, not company-evidence sources.

