from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

SignalStage = Literal["Early", "Emerging", "Process-confirmed"]
Transaction = Literal["sale_buyout", "ipo", "refinancing"]
SourceKind = Literal["registry", "company", "sponsor", "news", "trade", "unverified"]
CoverageKind = Literal["registry", "company", "ownership", "financial", "news"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Company(StrictModel):
    id: str
    name: str
    sector: str
    country: str
    profile: str
    ownership: str
    coverage: dict[CoverageKind, bool]
    illustrative: bool = True


class Evidence(StrictModel):
    id: str
    company_id: str
    event_id: str  # Canonical underlying event, shared by syndicated copies.
    event_date: date
    published_date: date
    observed_date: date
    signal_type: str
    strength: float = Field(ge=0, le=1)
    source_name: str
    source_family: str  # Shared editorial owner / originating source, not a domain count.
    source_kind: SourceKind
    is_original: bool = True
    source_url: str | None = None
    headline: str
    supporting_evidence: str
    illustrative: bool = True

    @model_validator(mode="after")
    def provenance(self):
        if self.observed_date < self.published_date:
            raise ValueError("Evidence cannot be observed before publication")
        if self.event_date > self.published_date:
            raise ValueError("Use announcement date as event date for forward-looking plans")
        if self.illustrative and self.source_url:
            raise ValueError("Illustrative evidence must not carry a fabricated source URL")
        if not self.illustrative and not (self.source_url or "").startswith(("https://", "http://")):
            raise ValueError("Real evidence requires a public source URL")
        return self

