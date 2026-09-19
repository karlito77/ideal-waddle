# ideal-waddle

## Risk Intelligence Platform (outline)

An outline application for a **community risk intelligence platform**. A
group of clients pool their insurance loss history, risk issues, IoT
signals and analytics on their own terms, and the platform uses the
pooled experience to drive each member's underlying risk model and their
**self-insured retention (SIR) decisions**.

```
pip install -e ".[dev]"
python scripts/demo.py            # full pipeline on a sample 3-client community
pytest                            # 22 tests
uvicorn riskintel.api.app:app     # REST API, docs at /docs
```

Read next:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): contexts, data flow, design decisions, what is real vs stubbed
- [docs/demo.html](docs/demo.html): interactive demo page built from the pipeline output (open in a browser)
- [docs/api-demo.html](docs/api-demo.html): step-through of the REST API with captured requests and responses
- [docs/API.md](docs/API.md): endpoint list and example requests
- [docs/ROADMAP.md](docs/ROADMAP.md): phased build-out

Package map:

```
riskintel/
  domain/       entities + enums (Client, LossEvent, RiskIssue, IoTSignal, SharingConsent, ...)
  ingestion/    loss runs, risk registers, device telemetry -> domain records
  community/    consent rules, peer cohorts, anonymised experience exchange
  analytics/    experience summary, trend, chain-ladder development, benchmarking
  modelling/    frequency/severity fit, issue + IoT modifiers, Monte Carlo, retention layering
  decisions/    SIR options table and recommendation against a risk appetite
  storage/      Repository interface (in-memory implementation)
  api/          FastAPI app and routers
  pipeline.py   runs one client through every step
  demo.py       deterministic sample community
```

---

Original note from the repo owner:

> Karl here and I'm new to all of this. Looking for great AI image recognition coding for food.
