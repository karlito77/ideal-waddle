# Risk Intelligence Platform: architecture outline

## Purpose

A shared platform for a community of clients (typically mid-to-large
corporates with meaningful self-insured risk) that:

1. takes in each client's **insurance loss history**, **risk issues** (own
   and shared by peers), **IoT / intelligence feeds**, and existing
   **analytics and loss models**;
2. lets clients **exchange experience data on their own terms** (by
   location, business activity, or any other cohort rule they accept);
3. uses the pooled experience to drive **underlying risk models** for each
   member;
4. turns those models into **self-insured retention (SIR) decisions** and
   feeds other processes (budgeting, captive feasibility, insurer
   negotiation, risk improvement prioritisation).

## Bounded contexts

| Context     | Package                | Responsibility |
|-------------|------------------------|----------------|
| Domain      | `riskintel.domain`     | Entities and enums shared by everything else. |
| Ingestion   | `riskintel.ingestion`  | Normalise loss runs, risk registers and device telemetry into domain records. |
| Community   | `riskintel.community`  | Consent, peer cohorts, anonymised exchange. |
| Analytics   | `riskintel.analytics`  | Experience statistics, trend, development, benchmarking. |
| Modelling   | `riskintel.modelling`  | Frequency/severity fit, modifiers, Monte Carlo, retention layering. |
| Decisions   | `riskintel.decisions`  | SIR options table and recommendation against a risk appetite. |
| Storage     | `riskintel.storage`    | Repository interface; in-memory now, database later. |
| API         | `riskintel.api`        | FastAPI surface over the pipeline. |

`riskintel.pipeline` is the spine that runs a client through every context
in order.

## Data flow

```
loss runs ─┐
risk reg. ─┼─ ingestion ─► repository ─► experience ─┐
IoT feeds ─┘                     │                   │
                                 │      peers + consent ─► pooled experience
                                 │                   │
                                 │              benchmark (credibility blend)
                                 │                   │
                            open issues ─► frequency/severity fit + modifiers
                            IoT coverage             │
                                               Monte Carlo aggregate
                                                     │
                                          retention layering per SIR
                                                     │
                                 risk appetite ─► SIR recommendation ─► other processes
```

## Key design decisions

**Consent belongs to the data owner.** The exchange checks the *peer's*
consent before any of the peer's records reach a requester, and applies
the peer's chosen anonymisation (aggregated bands, pseudonymised record
level, or identified) before the record leaves. Audiences are
whole-community, same-region cohort, or same-activity cohort. Revocation
is a timestamp, so history of what was shared when is preserved.

**Cohorts are computed, not configured.** Peer similarity scores activity
code prefix depth, region overlap and size ratio. Callers pick a
threshold. This keeps cohort logic explainable to a risk manager and easy
to extend with new dimensions (construction type, fleet size, and so on).

**Qualitative intelligence enters the model as modifiers.** Open risk
issues push frequency up by category; active IoT monitoring on a category
pulls it down. The modifiers are a small table so they can be calibrated
or replaced by a fitted GLM later without changing the pipeline.

**Credibility blends own and pooled experience.** Limited-fluctuation
credibility `Z = n / (n + k)` weights the client's own frequency and
severity against the pool. Small clients lean on the community; large
ones stand on their own data.

**Retention decisions are an options table, not a single number.** Every
candidate SIR gets expected retained, tail retained (P90/P95/P99), expected
ceded, a premium indication and total cost of risk. The recommendation is
the cheapest option that satisfies the client's risk appetite, with
reasons and the list of rejected options so the trade-off is visible.

## What is real in the outline and what is stubbed

Real, tested:
- domain validation, loss ingestion with dedupe and cause mapping
- IoT thresholds, alert promotion to issues
- consent enforcement, cohorts, anonymised pooling
- experience summary, trend, chain-ladder development
- frequency/severity fit, credibility blend, modifiers, Monte Carlo
- retention layering with aggregate cap, SIR recommendation
- REST API over all of it, in-memory storage, deterministic demo data

Outline only (interfaces exist, implementation is a placeholder):
- source adapters (CSV/XLSX loss runs, TPA APIs, MQTT / webhook device feeds)
- persistence (Postgres for records, warehouse for pooled analytics)
- authentication, tenancy and audit trail on data access
- model governance (versioned parameters, back-testing, approval)
- reporting and UI

## Non-functional notes

- **Tenancy and isolation**: each client's raw data stays in its own
  partition; only the exchange layer crosses the boundary, and only via
  consent. Audit every cross-tenant read.
- **Reproducibility**: simulations take a seed; model runs should be
  stored with parameters, seed, data snapshot and code version.
- **Scale**: the community is hundreds of clients, not millions; the
  expensive part is simulation, which parallelises trivially per client.
