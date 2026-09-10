"""Evaluation only for supplied, mature, point-in-time labels. No sample results."""
import argparse
import json
from datetime import timedelta
import pandas as pd


def evaluate(frame: pd.DataFrame, k: int, *, calibrated: bool = False) -> dict:
    """Evaluate one snapshot; use separate calls for successive out-of-time snapshots.

    Required: company_id, prediction_date, label_end_date, label, score.
    Label must cover the full 365-day horizon; any known outcome cannot be after it.
    A production evaluator must additionally enforce feature-availability lineage.
    """
    required = {"company_id", "prediction_date", "label_end_date", "label", "score"}
    if not required <= set(frame.columns) or frame.empty:
        raise ValueError("Nonempty CSV with required evaluation columns is needed")
    df = frame.copy()
    if df.company_id.duplicated().any():
        raise ValueError("One row per company per evaluation snapshot")
    df["prediction_date"] = pd.to_datetime(df.prediction_date, errors="raise")
    df["label_end_date"] = pd.to_datetime(df.label_end_date, errors="raise")
    if df.prediction_date.isna().any() or df.label_end_date.isna().any() or df.prediction_date.nunique() != 1:
        raise ValueError("Evaluate one complete prediction snapshot at a time")
    if ((df.label_end_date - df.prediction_date).dt.days < 365).any():
        raise ValueError("Labels must have 365 days of follow-up; immature negatives are censored")
    if not df.label.isin([0,1]).all() or not df.score.between(0,1).all():
        raise ValueError("Binary labels and finite scores in [0,1] required")
    if not 1 <= k <= len(df):
        raise ValueError("K must be between 1 and universe size")
    ranked = df.sort_values(["score","company_id"], ascending=[False,True])
    positives = int(df.label.sum())
    hits = int(ranked.head(k).label.sum())
    base_rate = positives / len(df)
    # Threshold groups handle ties; average precision is a step-integrated PR-AUC.
    grouped = ranked.groupby("score",sort=True).label.agg(["sum","count"]).sort_index(ascending=False)
    grouped["precision"] = grouped["sum"].cumsum() / grouped["count"].cumsum()
    ap = float((grouped["precision"] * grouped["sum"]).sum() / positives) if positives else None
    results = {"n":len(df),"k":k,"baseline_transaction_rate":base_rate,"precision_at_k":hits/k,"lift_at_k":(hits/k)/base_rate if positives else None,"recall_at_k":hits/positives if positives else None,"pr_auc_average_precision":ap,"brier_score":float(((df.score-df.label)**2).mean()) if calibrated else None,"brier_note":"Computed for supplied probabilities" if calibrated else "Omitted: ranking indices are not calibrated probabilities"}
    if "covered" in df:
        if not df.covered.isin([0,1]).all():
            raise ValueError("covered must be binary")
        results["coverage_rate"] = float(df.covered.mean())
    if "transaction_date" in df:
        transaction_dates = pd.to_datetime(df.transaction_date, errors="raise")
        days = (transaction_dates - df.prediction_date).dt.days
        if (df.label.eq(1) & (~days.between(1,365))).any() or (df.label.eq(0) & days.between(1,365)).any():
            raise ValueError("Transaction dates and 365-day labels disagree")
        results["median_lead_time_days_top_k_hits"] = float(days.loc[ranked.head(k).index].loc[df.label.eq(1)].median()) if hits else None
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--calibrated", action="store_true", help="Only for held-out calibrated probabilities")
    args = parser.parse_args()
    print(json.dumps(evaluate(pd.read_csv(args.csv),args.k,calibrated=args.calibrated),indent=2,allow_nan=False))
