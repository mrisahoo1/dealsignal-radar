# Scale and operating design

Validation path: **14 demo scenarios → 100-company shadow pilot → 100k universe**. The pilot is planned, not completed.

The demo intentionally recomputes a small file-based universe on interaction. It is not an architecture benchmark for 100,000 companies.

## Evolution path

| Stage | Practical design | Gate before expanding |
|---|---|---|
| 14 illustrative scenarios | CSV/JSON, typed validation, deterministic scoring and provenance UI | Correctness and explainability |
| 100-company shadow pilot | Permitted source adapters, scheduled deltas, persistent event/document history, analyst review | Source access, extraction quality, entity matches, useful queue |
| Larger selected markets | Queue/batch ingestion, incremental feature updates, robust source monitoring and historical labels | Out-of-time predictive lift and operating economics |
| Approximately 100k companies | Partitioned event/feature storage, incremental ranking, selective LLM processing, calibrated models | Commercial usefulness, reliable coverage and monitored cost |

## Pipeline components

**Source-specific adapters.** Prefer APIs, feeds and structured registry disclosures where lawfully available. Refresh high-value/changing sources more often and quiet profiles less often. Record connector version, rights/retention policy, retrieval time, source publication time, immutable document hashes and corrections. A source outage must lower confidence/coverage, not look like a quiet company.

**Change detection and processing.** Hash and cache documents; skip unchanged versions. Queue new documents in idempotent batches with bounded retries and failed-document review. Apply rate limits per source and adaptive schedules. Cheap structured-source parsing precedes language-model processing. Avoid repeated full crawling.

**Entity resolution.** Maintain legal identifiers, aliases, parent/subsidiary/sponsor links, country and historical effective dates. Use deterministic registry-ID/domain matches first; send ambiguous candidates to a scored resolver and review queue. Never merge solely on a fuzzy company-name match. Track entity-link confidence separately from propensity and preserve reversible merges.

**Selective AI.** Route only new, relevant unstructured documents to extraction. Deduplicate before paying for repeated articles. Use small-model extraction first; escalate complex, contradictory or low-quality outputs to a larger model or analyst based on measured extraction error. An LLM's self-reported certainty alone is not a sufficient routing criterion. Bound text length, enforce schemas, treat retrieved text as untrusted, validate quotes, and retain model/prompt versions. Do not send unrestricted full archives to a model by default.

**Event and feature store.** Store immutable document versions and attributable normalized events separately from time-aware derived features. Version extraction, weights and scoring models. Append retractions/corrections and recompute only affected companies. Retain enough lineage to replay any queue at its original scoring date. Use scalable storage later; no database server is needed for this demo.

**Propensity and calibration.** Begin with transparent rules and simple historical baselines. With mature labels, compare regularized logistic models and tree-based models on point-in-time features. Consider event-specific/time-to-event approaches for censored outcomes. Calibrate predicted probabilities on a separate forward window; preserve an independent evidence-confidence layer. Do not merge confidence into the probability label.

**Ranked coverage queue.** The demo uses propensity index × evidence confidence / 100 only as a prototype queue heuristic. The production concept is **transaction propensity → evidence-quality gate → commercial research priority**. Future commercial inputs are expected client demand, existing coverage gap/research freshness and available research capacity; none is implemented or simulated in the POC. Refresh only changed companies plus time-decay schedules. Validate transaction forecasts separately from commercial queue usefulness. Allow analysts to investigate, accept, override and record reasons. Separate accepted research ideas from eventual deal outcome labels.

## Monitoring

Monitor source availability, ingest latency, stale evidence, duplicate rates, entity-match error, schema/quote validation failures, extraction cost, model and feature drift, country/sector coverage, probability calibration and queue stability. Audit false positives and missed transactions with traceable document versions. Show model/version/as-of metadata. Protect a human review path and retain the last valid snapshot during an ingestion or extraction outage.

## Cost drivers

A useful budget equation is:

`new or changed documents × fraction requiring LLM extraction × tokens per document × model-routing mix`

Add source licensing/access, refresh frequency, structured parsing, document/event retention, queue compute, evaluation and analyst verification. The quantity of *new documents*, language complexity and text length can dominate variable inference cost; 100,000 companies with few updates is very different from 100,000 heavily covered companies. Measure per-source volume, cache-hit rate, extraction pass rate, escalations and cost per accepted research candidate during the pilot. Only then quote a budget or service-level target.

## Failure modes to defend in the interview

Direct reporting may be accurate but too late to create research advantage. Richly covered markets may monopolise the queue. A financing filing may describe an already completed event. A subsidiary can be mistaken for its parent. Several articles may share one anonymous source. A weak source can publish repeated distinct claims. Dynamic web pages can overwrite historical evidence. An elegant explanation can still justify an unvalidated score. Each requires evaluation and controls; none is solved by adding an agent framework.

Direct process signals may maximise precision but arrive too late. Test whether earlier, weaker readiness combinations yield lift with actionable lead time before expanding. The Signal stage label describes evidence maturity, not a probability or proof of an active process.
