import json
from .base import ExtractedEvent, ExtractionResult
from ..ingestion import load_config


class RulesExtractor:
    """Offline contract: validate already-normalized JSON, not pretend NLP."""
    def extract(self, text: str) -> ExtractionResult:
        rows = json.loads(text)
        if not isinstance(rows, list):
            raise ValueError("Normalized extraction input must be a JSON list")
        events = [ExtractedEvent.model_validate(row) for row in rows]
        config = load_config()
        for event in events:
            if event.signal_type not in config["signals"]:
                raise ValueError("Unknown signal type")
            rule = config["signals"][event.signal_type]
            if event.direction != rule["direction"]:
                raise ValueError("Signal direction conflicts with the taxonomy")
        return ExtractionResult(events=events, mode="normalized_fixture")
