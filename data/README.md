# Fixture and public-source policy

The shipped 14 companies and 49 evidence records are entirely illustrative. After merging three syndicated copies, 46 underlying events remain. Coincidental name similarities imply no relationship to any real organisation. Source names describe fictional source classes, not actual publications. Source URLs are null throughout. All dates are chosen to demonstrate recency at the fixed 2026-09-10 snapshot.

`companies.csv`: id, name, sector, country, profile, ownership, coverage (JSON object in a CSV cell), illustrative. Coverage keys are registry, company, ownership, financial, news; true means a source check is available in this scenario, not that it confirms a transaction.

`evidence.json`: an array validated against `src.models.Evidence`. Each record carries a unique evidence id, stable company id, canonical underlying event id, event/publication/first-observed dates, signal taxonomy key, strength 0–1, source name/family/kind, original-reporting flag, source URL, headline, supporting text and illustrative flag. Dates refer to the announcement or observation, not a future planned deal date. Strength is an analyst-assigned scenario assumption, not extracted truth.

Copies retain separate record IDs and publisher names but share the canonical event. A production source-family resolver must identify the original editorial/reporting family; site domains alone are not independent sources. The simple matcher handles canonical IDs and exact normalized text; it does not claim semantic deduplication or parent/subsidiary resolution.

Potential public-source adapters (not implemented or entitlement-verified here):

| Source class | Useful inputs | Important qualification |
|---|---|---|
| Official company disclosures | Reviews, finance hires, financial updates | Promotional bias; publication is not independent confirmation |
| Lawfully accessible company registries | Officers, ownership, filings, security/charges | Different filing delays and access rules; charges may describe completed ordinary borrowing |
| Public securities filings | Registration documents, structured disclosures | Form D is often ordinary fundraising, not a qualifying target transaction |
| Sponsor portfolio statements | Ownership start and portfolio status | Historical portfolio versions and sponsor entity mapping are necessary |
| Public business reporting | Sale processes, adviser engagement, credit mandates | Check original reporting and syndication, reporting lag and permitted excerpt use |
| Trade/sector publications | Operating changes and consolidation context | Usually weaker, non-company-specific evidence |

Before real ingestion: check terms/licensing, permitted storage/retention/model processing, robots/rate limits where applicable, geography and publication timeliness. Never bypass access controls. Preserve the URL, content hash, retrieval time and usable source excerpt under the applicable rights. Retracted or corrected articles require versioned evidence and re-scoring.

The prototype validator rejects illustrative evidence with a URL and real evidence without a public HTTP(S) URL. That validation is not a legal/ToS check or factual verification. Independently verify real evidence before loading it; never relabel a fictional record as factual.

Northmere Components is the default Emerging scenario. Its six fictional readiness events contain no strategic review, sale report, IPO preparation, refinancing mandate or adviser engagement. The fixture generator reproduces this case; all existing signal weights remain unchanged.
