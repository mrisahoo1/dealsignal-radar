"""Rebuild explicitly fictional scenarios. No network access and no real-company claims."""
import csv
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 10)
# signal, days old, source kind, source family, strength, supporting evidence
scenarios = [
("alderwick", "Alderwick Systems", "Enterprise software", "United Kingdom", "Sponsor-backed workflow software for industrial operators.", "Illustrative sponsor; held since 2018", [1,1,1,1,1], [
("strategic_review",12,"company","alderwick_press",1,"The board has launched a strategic alternatives review, including a potential sale of the business."),
("sponsor_tenure",45,"sponsor","sponsor_a",1,"An ownership update identifies the sponsor as controlling shareholder since 2018. Holding age is an indirect exit-readiness signal."),
("finance_hire",24,"registry","registry_uk",1,"A director appointment records a new finance leader with responsibility for reporting and governance."),
("sale_reporting",3,"news","business_wire_a",0.7,"An illustrative business report describes early buyer outreach. No binding agreement or completion date is reported."),
("growth",63,"trade","software_journal",0.8,"The company reports expansion into two new industrial end markets.")]),
("luma", "LumaForge Analytics", "Enterprise software", "United States", "Private data infrastructure vendor expanding enterprise distribution.", "Founder-led; growth-equity minority", [1,1,1,1,1], [
("ipo_preparation",8,"registry","registry_us",1,"A fictional public registration filing describes proposed listing preparations. Timing and pricing remain subject to review."),
("finance_hire",32,"company","luma_press",1,"The company announced a new CFO with listed-company reporting experience."),
("growth",51,"news","business_wire_b",0.9,"An independent report describes expansion of enterprise contracts and operating capacity."),
("fundraise",120,"sponsor","sponsor_b",0.7,"A routine growth round funded capacity expansion. This financing is an input signal, not a qualifying target event.")]),
("stonehaven", "Stonehaven Packaging", "Industrials", "Germany", "Specialist packaging producer with a leveraged capital structure.", "Illustrative sponsor-backed business", [1,1,1,1,1], [
("refinancing_mandate",6,"news","credit_wire",1,"A public report describes a lender mandate to refinance existing facilities. No completed refinancing is assumed."),
("debt_maturity",27,"company","stone_press",1,"A company financial disclosure identifies a material debt facility maturing within nine months."),
("board_change",70,"registry","registry_de",0.8,"A registry notice records an additional finance-focused director."),
("growth",38,"trade","packaging_journal",0.7,"A sector publication reports that the producer expanded a contracted production line.")]),
("vesper", "Vesper Harbor Health", "Healthcare", "United States", "Regional outpatient services network with sparse public reporting.", "Ownership not verified", [0,0,0,0,1], [
("sale_reporting",2,"unverified","single_origin",1,"A single uncorroborated illustrative article claims a sale process is being considered. No company statement or registry corroboration is available.")]),
("northmere", "Northmere Components", "Industrials", "United Kingdom", "Precision components producer supplying industrial equipment firms.", "Illustrative sponsor; held since 2019", [1,1,1,0,1], [
("sponsor_tenure",21,"sponsor","sponsor_c",1,"A fictional sponsor portfolio update confirms a controlling investment held since 2019. Mature ownership is an exit-readiness indicator, not evidence of a sale mandate."),
("finance_hire",14,"company","north_press",1,"A new CFO has been appointed to strengthen financial reporting and integration. No transaction mandate or timetable is announced."),
("board_change",9,"registry","registry_uk",1,"A fictional registry notice records two independent board appointments with governance and audit responsibilities. No change of control is recorded."),
("new_charge",12,"registry","registry_uk",0.9,"A new security filing covers an operating facility. This may reflect ordinary borrowing; no refinancing process is announced."),
("growth",26,"news","industrial_wire",0.9,"Independent illustrative reporting describes a contracted capacity expansion into a second industrial end market. The report identifies no transaction process."),
("consolidation",18,"trade","components_journal",0.9,"A sector review describes consolidation among comparable suppliers. This is contextual evidence, with no company-specific sale reporting.")]),
("cairn", "Cairnlight Logistics", "Business services", "France", "Contract logistics operator with a concentrated lender base.", "Family-owned", [1,1,0,1,1], [
("debt_maturity",92,"company","cairn_press",0.8,"A fictional annual disclosure lists a material facility due within the next twelve months."),
("new_charge",19,"registry","registry_fr",0.8,"A public charge notice describes new security over operating assets; it may relate to ordinary financing."),
("steady_trading",43,"news","logistics_wire",1,"Operating updates describe stable volumes with no announced strategic process.")]),
("morrow", "Morrowfield Digital", "Enterprise software", "United Kingdom", "Vertical software group with conflicting transaction reports.", "Illustrative sponsor-backed business", [1,1,1,0,1], [
("sale_reporting",25,"news","business_wire_d",0.85,"A public report claims exploratory discussions with potential acquirers; no formal agreement is described."),
("sale_denied",4,"company","morrow_press",1,"The company explicitly denies an active sale process and says it remains focused on standalone execution."),
("sponsor_tenure",53,"sponsor","sponsor_d",0.9,"The sponsor discloses a mature holding period in its portfolio update."),
("finance_hire",80,"registry","registry_uk",0.7,"A new finance director appointment is recorded.")]),
("tessel", "Tesselbrook Networks", "Enterprise software", "Germany", "Network operations software serving midsized businesses.", "Founder-led", [1,1,0,0,1], [
("ipo_preparation",180,"news","tech_wire",0.65,"An earlier report described possible listing preparations without a public filing."),
("finance_hire",54,"company","tessel_press",0.9,"A new CFO is appointed to strengthen reporting processes."),
("board_change",40,"registry","registry_de",0.8,"Independent board appointments are recorded.")]),
("bracken", "Brackenvale Foods", "Consumer", "France", "Established private ingredients manufacturer.", "Family-owned", [1,1,1,1,1], [
("steady_trading",10,"company","bracken_press",1,"The company describes stable trading and routine operating investment without a strategic transaction announcement."),
("debt_runway",38,"news","food_wire",1,"Reporting describes existing debt with a long maturity runway beyond the forecast horizon."),
("board_change",75,"registry","registry_fr",0.3,"A routine director succession is recorded without an ownership change."),
("consolidation",44,"trade","food_journal",0.3,"Broad ingredients sector consolidation continues; no company-specific deal intent is identified.")]),
("orbital", "Orbelune Diagnostics", "Healthcare", "United States", "Early-stage diagnostic platform developing laboratory capacity.", "Venture-backed", [0,1,1,0,1], [
("fundraise",21,"company","orbel_press",1,"A routine venture funding round supports laboratory development; there is no sale, listing or material debt restructuring announcement."),
("growth",71,"trade","health_journal",0.7,"A laboratory expansion is described by a specialist publication."),
("steady_trading",41,"sponsor","sponsor_e",1,"An investor update describes a multiyear product-development plan.")]),
("elm", "Elmridge Materials", "Industrials", "Germany", "Private materials supplier with limited recent disclosure.", "Ownership not verified", [0,1,0,0,0], [
("growth",340,"company","elm_press",0.7,"An old company update describes a modest production expansion. No recent company-specific transaction evidence is available.")]),
("solenne", "Solenne Field Services", "Business services", "United Kingdom", "Field maintenance network serving commercial facilities.", "Founder-owned", [1,1,1,1,1], [
("steady_trading",12,"company","sol_press",1,"A trading statement describes stable contracts and routine capital spending."),
("sale_denied",22,"news","service_wire",1,"A public interview explicitly rules out a sale process within the current strategic plan."),
("debt_runway",47,"registry","registry_uk",0.9,"A filing records an existing facility whose scheduled maturity lies outside the forecast horizon."),
("steady_trading",35,"trade","service_journal",1,"Sector coverage describes steady service demand and no company-specific transaction catalyst.")]),
("arden", "Ardenvale Commerce", "Consumer", "United States", "Private commerce platform whose listing timetable has changed.", "Growth-equity backed", [1,1,0,1,1], [
("ipo_preparation",150,"news","retail_wire",0.8,"An earlier report described listing preparations, with no binding timetable."),
("ipo_delayed",11,"company","arden_press",1,"A company statement postpones listing plans beyond the next twelve months."),
("finance_hire",110,"registry","registry_us",0.6,"A financial officer appointment is recorded.")]),
("fen", "Fenwick Reach", "Business services", "France", "Small private operations provider with almost no public coverage.", "Ownership not verified", [0,0,0,0,1], [
("steady_trading",280,"trade","local_journal",0.5,"An old directory profile describes ordinary service operations, without financial or transaction detail.")])
]
companies, events = [], []
for cid, name, sector, country, profile, ownership, coverage, entries in scenarios:
    companies.append(dict(id=cid, name=name, sector=sector, country=country, profile=profile, ownership=ownership, coverage=json.dumps(dict(zip(["registry","company","ownership","financial","news"], map(bool,coverage)))), illustrative=True))
    for number, (signal, age, kind, family, strength, evidence) in enumerate(entries, 1):
        stamp = (AS_OF - timedelta(days=age)).isoformat()
        events.append(dict(id=f"{cid}-e{number:02d}", company_id=cid, event_id=f"{cid}-event-{number:02d}", event_date=stamp, published_date=stamp, observed_date=stamp, signal_type=signal, strength=strength, source_name=f"Illustrative {kind} record", source_family=family, source_kind=kind, source_url=None, headline=signal.replace("_", " ").capitalize(), supporting_evidence=evidence, illustrative=True))
# Three syndicated copies of the same sparse company's report must not raise scores.
original = next(e for e in events if e["company_id"] == "vesper")
for i in range(1,4):
    events.append({**original, "id": f"vesper-copy-{i}", "source_name": f"Illustrative syndicated copy {i}", "source_family": f"copy_publisher_{i}", "is_original": False})
with (ROOT / "data/companies.csv").open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(companies[0]))
    writer.writeheader()
    writer.writerows(companies)
(ROOT / "data/evidence.json").write_text(json.dumps(events, indent=2), encoding="utf-8")
print(f"Wrote {len(companies)} fictional companies, {len(events)} evidence records.")

