# Roadmap

## Phase 1: foundation (this outline)
- Domain model, ingestion, consent, cohorts, analytics, modelling, SIR decision, API.
- In-memory storage, demo community, test suite.

## Phase 2: real data in
- Loss-run adapters: CSV/XLSX templates for the common broker/TPA formats; mapping UI for columns.
- Risk register import (spreadsheet + API) and assessor report intake.
- IoT connectors: MQTT and webhook receivers; device registry; per-client threshold overrides.
- Postgres persistence behind the `Repository` interface; migration tooling.
- Authentication (OIDC), per-client roles, audit log of every cross-tenant read.

## Phase 3: better models
- Fit severity by line of business and cause, not one distribution per client.
- Development on transaction-level triangles; IBNR loading on open years.
- Replace the modifier table with a calibrated GLM on pooled experience plus issue and IoT features.
- Correlation between lines / locations in simulation (copula or common shock).
- Model registry: versioned parameters, back-tests, sign-off workflow.

## Phase 4: decisions and processes
- SIR decision reports (PDF/HTML) with the options table and reasons.
- Aggregate stop-loss and corridor structures; captive feasibility view.
- Budget and collateral projections from the retained-loss distribution.
- Risk improvement prioritisation: which open issues move expected loss most.
- Insurer renewal pack: experience, benchmark, modelled layers.

## Phase 5: community features
- Cohort builder UI for custom sharing rules.
- Benchmark dashboards by region, activity, cause.
- Anonymised issue library with adoption tracking (which peer issues helped whom).
- Data-quality scoring so the pool weights reliable contributors higher.
