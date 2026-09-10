from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_offline_app_filters_details_and_empty_state():
    app = AppTest.from_file(str(ROOT / "app.py"),default_timeout=20).run()
    assert not app.exception
    assert app.selectbox(key="detail_company").value == "northmere"
    columns = set(app.dataframe[0].value.columns)
    assert {"Propensity index", "Evidence confidence", "Signal stage"} <= columns
    assert "Confidence" not in columns and "12m propensity" not in columns
    text = " ".join(item.value for item in app.markdown)
    assert "Demo scenarios" in text and "Companies monitored" not in text
    assert "No public transaction process identified" in text
    assert "14 demo scenarios → 100-company shadow pilot → 100k universe" in text
    assert "commercial priority" in text
    assert list(app.dataframe[0].value["Company"])[0] == "Alderwick Systems"
    assert "Signal stage: Emerging" in text
    app.selectbox(key="detail_company").set_value("vesper").run()
    assert not app.exception
    assert any("4 source records" in item.value for item in app.markdown)
    app.selectbox[0].select("Germany").run()
    assert not app.exception
    assert set(app.dataframe[0].value["Country"]) == {"Germany"}
    app.selectbox[1].select("Enterprise software").run()
    app.selectbox[2].select("IPO").run()
    assert list(app.dataframe[0].value["Company"]) == ["Tesselbrook Networks"]
    app.selectbox(key="detail_company").set_value("vesper").run()
    assert app.selectbox(key="detail_company").value == "vesper"
    app.slider[0].set_value(100).run()
    assert not app.exception
    assert any("No companies match" in item.value for item in app.info)

