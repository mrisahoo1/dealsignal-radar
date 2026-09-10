# Verification record

Refinement pass verified locally on 10 September 2026 with the existing Python 3.11 / Streamlit 1.63.0 environment. No dependencies, scoring weights, confidence formula or queue thresholds were changed.

- Complete suite: `python -m pytest -q` — **40 passed**. Stage tests cover all four process signals; Emerging readiness; sparse, stale and uncorroborated evidence; category/source/type thresholds; negative evidence; high score without process; and honest default ranking. UI tests check the requested labels, default company, combined filters and empty state.
- Restarted the existing project Streamlit server on `http://127.0.0.1:8501` to clear old imported modules. Health endpoint returns **HTTP 200, ok**. Fresh app loading and the complete UI were verified after the restart.
- Actual browser inspection at **1440×900**, default filters: **Northmere Components** is selected and highlighted at **rank #5**, with **Emerging**, **54.5/100 Propensity index**, **91.5/100 Evidence confidence**, and **Priority 2 — analyst review**. Its queue heuristic is 49.9. The table is still sorted by the actual heuristic, not by the screenshot selection.
- Northmere has six distinct readiness signal types, five categories and five independent source families. Its events are mature sponsor holding, finance leadership change, board/governance change, new security/charge filing, operating expansion and sector consolidation. **No process-level signal or adviser engagement is present.**
- Default Why now explicitly says **No public transaction process identified** and notes the missing financial source check. Score displays use consistent one-decimal indices; coverage remains a percentage.
- Visually confirmed **Propensity index**, **Evidence confidence** and **Signal stage** headers. The two indices use different colours. **Demo scenarios = 14** replaces the old universe KPI. No Streamlit Deploy control/toolbar appears; OFFLINE DEMO and app navigation remain visible.
- Opened Methodology in the browser and verified **Validation path: 14 demo scenarios → 100-company shadow pilot → 100k universe**. Confirmed transaction propensity → evidence-quality gate → commercial research priority, with client demand, coverage gap/freshness and capacity explicitly marked as future inputs, not implemented data.
- Clicked another table row and verified LumaForge replaced the default in Evidence explorer, with Process-confirmed stage and attributable event records. Selected Vesper through the dropdown to refresh the existing low-confidence evidence screenshot, then returned the browser to the default view.
- All 49 shipped source records remain fictional with null public URLs. There are 46 underlying events across the same 14 companies; extra Northmere evidence does not inflate the company count. The optional LLM seam and offline path remain intact.

Primary screenshot: `output/playwright/dealsignal-radar-1440x900.png`.
Secondary evidence screenshot: `output/playwright/evidence-low-confidence.png`.

These checks establish runtime correctness and scenario behaviour, not predictive lift. Stage thresholds are hypotheses. Process-confirmed describes qualifying observed process evidence, not certainty that a process remains active or a deal will occur. The 100-company pilot is planned, not completed. Historical point-in-time backtesting and commercial workflow validation remain necessary.
