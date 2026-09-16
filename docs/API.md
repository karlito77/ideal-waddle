# API outline

Run locally:

```
pip install -e ".[dev]"
uvicorn riskintel.api.app:app --reload
```

Interactive docs at `http://localhost:8000/docs`.

| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/health` | liveness |
| POST | `/communities` | create a community |
| POST | `/clients` | register a client (locations, activity code, communities) |
| GET  | `/clients`, `/clients/{id}` | list / fetch |
| POST | `/clients/{id}/exposures` | exposure base per year |
| POST/GET | `/clients/{id}/consents` | data-sharing consent |
| POST | `/losses` | bulk loss-run ingestion (dedupe + cause mapping) |
| GET  | `/losses/{client_id}` | raw loss events |
| GET  | `/losses/{client_id}/experience` | trended frequency/severity summary |
| GET  | `/losses/{client_id}/development` | incurred triangle + chain-ladder |
| POST | `/risk-issues` | raise an issue (own / assessor / peer / iot / model) |
| GET  | `/risk-issues/{client_id}` | issues ranked by score |
| GET  | `/risk-issues/{client_id}/peer` | issues peers have agreed to share |
| POST | `/risk-issues/{client_id}/adopt/{origin_issue_id}` | copy a peer issue into own register |
| POST | `/iot/signals` | device telemetry; derives alerts and promotes repeats to issues |
| GET  | `/iot/{client_id}/alerts` | alerts |
| GET  | `/community/{client_id}/peers` | cohort matches |
| GET  | `/community/{client_id}/pool` | anonymised pooled losses visible to this client |
| GET  | `/community/{client_id}/benchmark` | own vs pool with credibility blend |
| POST | `/models/{client_id}/fit` | fitted model + aggregate loss distribution |
| POST | `/decisions/{client_id}/sir` | SIR options table and recommendation |

Example SIR request:

```json
{
  "candidate_sirs": [25000, 50000, 100000, 250000],
  "appetite": {"max_retained_p99": 1500000, "volatility_weight": 0.5},
  "aggregate_cap": null,
  "trials": 10000
}
```
