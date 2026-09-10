from datetime import date
from typing import Callable, Literal, Protocol
from pydantic import Field
from ..models import StrictModel, Transaction


class ExtractedEvent(StrictModel):
    company: str
    event_date: date
    signal_type: str
    transaction_type_relevance: list[Transaction]
    direction: Literal[-1, 1]
    strength: float = Field(ge=0, le=1)
    entities: list[str]
    supporting_evidence: str
    reason: str
    uncertainty: str


class ExtractionResult(StrictModel):
    events: list[ExtractedEvent]
    mode: Literal["normalized_fixture", "llm", "fallback"]
    warning: str | None = None


class Extractor(Protocol):
    def extract(self, text: str) -> ExtractionResult: ...


Transport = Callable[[str, dict], str]
