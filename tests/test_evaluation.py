import pandas as pd
import pytest
from src.evaluation import evaluate


def sample():
    return pd.DataFrame({"company_id":["a","b","c","d"],"prediction_date":["2024-01-01"]*4,"label_end_date":["2025-01-01"]*4,"label":[1,0,1,0],"score":[.9,.8,.5,.1]})


def test_known_ranking_metrics_and_explicit_calibration_opt_in():
    result = evaluate(sample(),2)
    assert result["precision_at_k"] == .5
    assert result["recall_at_k"] == .5
    assert result["lift_at_k"] == 1
    assert result["pr_auc_average_precision"] == pytest.approx((1+2/3)/2)
    assert result["brier_score"] is None
    assert evaluate(sample(),2,calibrated=True)["brier_score"] == pytest.approx(.2275)


def test_reject_censored_labels_future_outcomes_and_bad_scores():
    for column,value in [("label_end_date","2024-04-01"),("score",float("nan")),("label",2)]:
        data = sample()
        data.loc[0,column] = value
        with pytest.raises(ValueError): evaluate(data,2)
    data = sample()
    data["transaction_date"] = ["2024-02-01",None,"2026-01-01",None]
    with pytest.raises(ValueError): evaluate(data,2)


def test_ties_and_no_positives():
    data = sample()
    data["score"] = .5
    assert evaluate(data,2)["pr_auc_average_precision"] == .5
    data["label"] = 0
    assert evaluate(data,2)["recall_at_k"] is None


def test_lead_time_and_coverage():
    data = sample()
    data["transaction_date"] = ["2024-02-01",None,"2024-06-01",None]
    data["covered"] = [1,0,1,1]
    result = evaluate(data,3)
    assert result["median_lead_time_days_top_k_hits"] == 91.5
    assert result["coverage_rate"] == .75
