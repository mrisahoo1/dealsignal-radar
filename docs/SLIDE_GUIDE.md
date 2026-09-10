# Three-slide narrative guide

The assignment PDF imposes a hard maximum of three slides. This is an outline, not a generated presentation. The repository and two-minute demo are supporting material.

## Slide 1 — Surface companies before the transaction becomes obvious

Executive message: “Direct signals improve precision; combinations of weaker early signals may create lead time.”

Forecasting question: Which private companies show evidence of entering a material transaction within the next ~12 months?

Show **public sources → change detection + entity resolution → structured event extraction → signal store → transaction propensity → evidence-quality gate → commercial research priority → analyst feedback**. LLMs structure attributable events; deterministic logic and eventually validated models aggregate and monitor them. Preserve source rights, deduplication and lineage. Future commercial inputs: client demand + coverage gap/freshness + capacity, explicitly not implemented.

Validation path: **14 demo scenarios → 100-company shadow pilot → 100k universe**. The 14 cases validate behaviour/UI. The planned point-in-time pilot validates coverage and workflow before scaling. It has not been completed.

## Slide 2 — Test lead time separately from commercial usefulness

Executive message: “Earlier, weaker signals are useful only if they deliver sufficient lift with time to act.”

Direct process signals are likely to maximise precision but may arrive too late to create useful research lead time. The key validation question is whether combinations of earlier, weaker signals create sufficient lift while preserving actionable lead time. Compare Emerging versus Process-confirmed cohorts on forward historical holdouts using Precision/Lift@K and lead time; calibrate only with valid labels.

Commercial action question: Given transaction propensity and evidence quality, where should Third Bridge deploy scarce research capacity? This differs from forecasting. Measure analyst acceptance and later research consumption as separate commercial outcomes. The POC's propensity index × evidence confidence / 100 is a transparent **prototype queue heuristic**, not the final production prioritisation function.

Highest-risk assumptions: historical evidence/label availability, geographical source coverage, entity resolution, source rights and predictive value. The POC demonstrates mechanics, not predictive performance.

## Slide 3 — DealSignal Radar: an Emerging warning with an evidence trail

Use `output/playwright/dealsignal-radar-1440x900.png`. Northmere Components is selected by default at its honest rank #5: **Emerging**, **54.5/100 Propensity index**, **91.5/100 Evidence confidence**, **Priority 2 — analyst review**. No public transaction process is identified. Its six readiness signals contain no sale process, strategic review, IPO preparation, refinancing mandate or adviser engagement.

Callouts: Signal stage; independent evidence confidence; traceable Why now and proposed research action. The index remains below 60 because the existing weights were preserved—not adjusted to improve the screenshot. A lower index can still merit early analyst attention.

Keep the demo-data disclaimer, stage and index labels visible. Do not turn either index into a percentage probability. Process-confirmed describes qualifying observed evidence, not assurance that a process is active or that a deal will occur. This is fictional output, not measured forecasting lift.
