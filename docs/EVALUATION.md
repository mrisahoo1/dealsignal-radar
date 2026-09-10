# Evaluation: prove usefulness before probabilities

No predictive evaluation results are claimed. The fixture was designed to exercise behaviour, not sampled to estimate performance.

## Target and observation unit

One company at one prediction date t. Label 1 if the first public announcement of a qualifying material sale/acquisition/control buyout, IPO or refinancing/recapitalisation occurs in (t, t+365 days]; otherwise label 0 only after adequate follow-up. Agree materiality and event boundaries with research teams before collection. In particular, distinguish IPO preparation/registration from the qualifying IPO announcement, and a financing mandate from a completed or definitively announced recapitalisation. Ordinary funding is not automatically a positive label.

Exclude companies with already-announced qualifying transactions from the at-risk universe. Do not reward the system for predicting closing after an announced sale. A sale-process article may be an early signal, but check the article against the label source to ensure it does not already disclose the target event. Record cancellations and repeat deals separately. Evaluate event-specific heads and the any-transaction outcome without double counting one company.

## Point-in-time construction

1. Build monthly historical company-universe snapshots, including inactive/quiet companies and disappeared firms, not just eventual deal companies.
2. Reconstruct only source content, entity links and source-coverage assessments available at t. Store event date, original publication date, retrieval/first-observed date and document versions. Use the later availability time for eligibility, never a backfilled event date alone.
3. Join outcomes independently. Positive labels need a sourced event and date; negatives need mature follow-up. Treat lost coverage and incomplete follow-up as censored, not confirmed negatives.
4. Split chronologically into training, calibration/validation and an untouched forward test period. Purge overlapping 365-day outcome windows at boundaries and embargo as needed. Prevent duplicate articles and the same deal from straddling folds; report sensitivity to holding out company/sponsor groups.
5. Lock taxonomy/weights/model selection using training and validation only. Evaluate rolling forward test snapshots, including different market regimes. A coverage flag known today must not be used in an old snapshot.

This prototype's eligibility filter excludes future publication/observation, but its static company coverage flags are **not historical snapshots**. It must not be used directly to claim point-in-time backtest validity. Historical source versions and coverage history are required first.

## Metrics and baselines

| Measure | Decision it informs |
|---|---|
| Precision@K | Of the analyst-capacity-sized queue, how many companies transact? |
| Lift@K | Improvement versus the same-date universe base rate and simple sector/ownership/coverage baselines |
| Recall@K | How much eventual deal activity can this coverage budget capture? |
| PR-AUC | Ranking quality across thresholds in a low-base-rate problem; specify integration convention |
| Brier score and reliability plots | Whether held-out probabilities match observed frequencies; never interpret a rules index as calibrated |
| Lead time | Days from first useful flag to qualifying event, with distribution and repeated-alert accounting |
| Coverage rate | Eligible companies with adequate source availability; audit missingness separately from score |

Report by country, sector, ownership, company size, deal type and source density. Compare to random selection and a pragmatic analyst/sponsor-tenure baseline. Test ablations: direct reporting only, no LLM extraction, no interactions, and exclusion of last-minute process reporting. Bootstrap by company/time blocks to quantify uncertainty. K follows research capacity; do not select it after seeing the test outcomes.

### Implemented utility

`python -m src.evaluation labelled_snapshot.csv --k 20`

Required columns: `company_id,prediction_date,label_end_date,label,score`. Supply one row per company and exactly one prediction snapshot per file. Score must be a finite 0–1 ranking value. `label_end_date` documents at least 365 days of observed outcome follow-up. Optional `covered` is binary. Optional `transaction_date` must agree with positive/negative labels within the horizon.

The utility computes Precision@K, Lift@K versus universe base rate, Recall@K and step-integrated PR-AUC (average precision, tied scores grouped). Company ID is the deterministic top-K tie-breaker. With zero positives, undefined lift/recall/PR-AUC return null. `--calibrated` explicitly enables Brier score for supplied probabilities. Coverage and median top-K-hit lead time appear when their inputs are supplied.

The evaluator validates arithmetic inputs and label consistency. It does not fetch outcomes, reconstruct historical source availability, train or calibrate a model, certify a caller's probabilities, generate reliability plots, or calculate confidence intervals. Those are the next evaluation steps, not demonstrated features. Unit-test arrays only check mathematical correctness.

## Early-warning evaluation by signal stage

Direct process signals are likely to maximise precision but may arrive too late to create useful research lead time. The key validation question is whether combinations of earlier, weaker signals create sufficient lift while preserving actionable lead time. Compare Early, Emerging and Process-confirmed cohorts at the same prediction date, using stage computed only from then-available evidence. Measure first-alert lead time and Precision/Lift@K with and without explicit process signals, controlling for source coverage and sector. Do not treat a company becoming Process-confirmed as an outcome label; use the independently sourced qualifying transaction.

Stage thresholds are unvalidated hypotheses. The Emerging fixture demonstrates intended behaviour, not learned forecasting skill. Negative evidence cannot itself advance stage. Process-confirmed means qualifying process evidence was observed; an explicit denial or postponement can still make the current transaction hypothesis weak.

## Commercial evaluation and rollout gate

The forecasting question is: which private companies show evidence of entering a material transaction within the next ~12 months? The commercial action question is: given transaction propensity and evidence quality, where should Third Bridge deploy scarce research capacity? Evaluate these related questions separately.

The implemented propensity index × evidence confidence / 100 is a **prototype queue heuristic**. A mature workflow would use transaction propensity → evidence-quality gate → commercial research priority, adding expected client demand, existing coverage gaps/research freshness and available capacity. Those commercial inputs are not implemented. Assess future demand models and queue policies separately from transaction prediction; research usage is not a transaction label.

Validation path: **14 demo scenarios → 100-company shadow pilot → 100k universe**. The fictional scenarios validate behaviour/UI; the planned point-in-time pilot validates source coverage and workflow before scaling. No pilot results are claimed.

Run a shadow pilot against business-as-usual with comparable analyst capacity. Have analysts judge usefulness before seeing outcomes. Record accepted/rejected/overridden rankings with reasons, time spent verifying evidence, research commissioned, time to publication, and later consumption when client demand arrives. Capture false-positive opportunity cost and missed-company reviews.

Success means useful proactive research arriving early enough to meet demand. Track analyst acceptance/override rates, research consumption conditional on later demand, and time saved versus verification burden. Use matched cohorts or a randomized queue trial if operationally feasible; higher consumption alone can reflect attention bias. Feedback is an operational label, not proof of an eventual transaction.

Only after defensible lift, useful lead time, coverage equity, acceptable source rights/cost and commercial benefit should the system graduate from a 100-company pilot. Probability calibration and automated commissioning thresholds require separate sign-off based on evidence.
