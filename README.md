# Omni Backlink Gap Analysis

An end-to-end ETL + dbt + semantic-layer pipeline answering:

> **Which high-value backlink opportunities should Omni investigate,
> based on competitor backlink patterns?**

It mines the Common Crawl **domain webgraph** (release
`cc-main-2026-apr-may-jun`, which aggregates the May
`CC-MAIN-2026-21` and June `CC-MAIN-2026-25` collections) for
referring domains that link to Omni's competitors — **Sigma, Hex,
Mode, Metabase** — but *not* to Omni, scores them on
consensus × authority, gates them through a bounded LLM relevance
pass, and publishes a top-25 opportunity list for Growth Marketing.

Full design rationale, decision log, and contracts:
**[TECH_SPEC_DRAFT.md](TECH_SPEC_DRAFT.md)**.

## Deliverables map

| Assignment deliverable | Where |
|---|---|
| ETL framework + code | [`pipeline/`](pipeline/) (Python: extract, transform, enrich stages + retry manifest) |
| dbt project | [`dbt/`](dbt/) (staging → intermediate → marts; tests + enforced contract) |
| Omni semantic model | *lands in build step 6 — see spec §9* |
| Top-25 report | *lands in build step 5 — see spec §9* (will be committed under `artifacts/`) |
| Tech Spec | [`TECH_SPEC_DRAFT.md`](TECH_SPEC_DRAFT.md) |

## Prerequisites

- **macOS or Linux**, Python managed by **[uv](https://docs.astral.sh/uv/)**
  (`curl -LsSf https://astral.sh/uv/install.sh | sh`) — uv fetches the
  pinned Python 3.12 automatically
- **make** (preinstalled on macOS/Linux)
- **~20 GB free disk** (17.9 GB one-time Common Crawl download + DuckDB warehouse)
- *(Optional)* **`ANTHROPIC_API_KEY`** — only to *regenerate* LLM
  classifications; **not required to run or review** (see below)

## Quickstart

```bash
git clone https://github.com/wju99/omni.git && cd omni
make setup      # install pinned deps into .venv (uv.lock)
make run        # full pipeline: extract → transform → enrich → finalize
```

First run downloads ~17.9 GB from Common Crawl (bandwidth-bound,
~15–40 min) then builds everything else in minutes. Re-runs are
incremental: completed work is skipped via the manifest.

### Running without an API key (the default review path)

The enrich stage detects a missing `ANTHROPIC_API_KEY` and runs as an
explicit **DRY RUN** — a loud banner, **zero API calls, zero cost** —
bootstrapping the LLM classifications from the committed
[`artifacts/enrichment_cache.csv`](artifacts/). The entire pipeline
reproduces end-to-end **with no credentials at all**.

### Running with an API key (regeneration)

```bash
cp .env.example .env    # add ANTHROPIC_API_KEY=sk-ant-...
make run
```

Classifies only *uncached* shortlist domains with `claude-haiku-4-5`
(structured outputs, `temperature=0`). Full regeneration of ~150
domains costs **~$0.10–0.50, one-time** (cache-by-domain thereafter).

## Pipeline stages & commands

| Command | What it does |
|---|---|
| `make setup` | Install pinned dependencies (`uv.lock`) |
| `make run` | All stages, in order, resumable end-to-end |
| `make extract` | Download webgraph (64 MiB resumable chunks) + load `raw.*` into DuckDB |
| `make transform` | `dbt build` — seeds, 9 models, 29 tests, enforced contract |
| `make enrich` | LLM relevance/category pass (DRY RUN without key) |
| `make status` | Manifest progress + warehouse table counts |
| `make test` | Python unit tests (manifest, chunking, cache round-trip) |
| `make clean-db` | Drop the warehouse file (downloads are kept) |

Every command is idempotent — safe to re-run, safe to schedule.
(Direct CLI: `uv run python -m pipeline <init|status|extract|transform|enrich|reset|run>`.)

## Validating the system (reviewer checklist)

**1. Unit tests** — `make test`: manifest claim/resume semantics,
download chunk planning, enrichment-cache round-trip.

**2. Data tests & contracts** — `make transform` runs 29 dbt checks,
including:
- the **thesis test**: no domain in the gap set links to Omni
  (`dbt/tests/assert_no_gap_domain_links_to_omni.sql`)
- an **enforced model contract** on `top_backlink_opportunities`
  (12 typed columns — schema drift fails the build)
- uniqueness/nullability on every layer's keys

**3. Retry & recovery semantics (spec B9)** — kill any stage
mid-flight (`Ctrl-C` during the download is the dramatic one), then
`make run`: the manifest resumes at the first incomplete unit.
Inspect with `make status`; force a redo with
`uv run python -m pipeline reset <stage>`.

**4. Reproducibility** — pinned crawl release ID · pinned deps
(`uv.lock`, committed) · pinned model ID + `temperature=0` +
JSON-schema-enforced output shape · committed enrichment cache with
`model`/`enriched_at` provenance. Two runs from a clean clone produce
the same top-25.

**5. Inspect the warehouse directly**

```bash
uv run python -c "
import duckdb
con = duckdb.connect('data/omni.duckdb', read_only=True)
print(con.execute('''
    select domain, competitor_consensus, harmonic_pos,
           round(opportunity_score, 3) as score
    from marts.backlink_opportunities
    order by opportunity_score desc limit 10''').fetchall())"
```

## Repo layout

```
pipeline/            Python package: config, DuckDB + manifest, stages
  config.py          release ID, targets, URLs, paths (single source of truth)
  db.py              warehouse bootstrap + pipeline_manifest (retry backbone)
  extract.py         chunked resumable download + filtered raw load
  transform.py       dbt build wrapper
  enrich.py          Haiku 4.5 structured-outputs classification + cache
dbt/                 dbt project (profiles.yml: local dev / MotherDuck prod)
tests/               pytest suite
artifacts/           committed pipeline outputs (enrichment cache, report)
data/                gitignored: 17.9 GB downloads + omni.duckdb warehouse
Makefile             the operator interface
TECH_SPEC_DRAFT.md   decision log + contracts + tradeoffs + recovery semantics
```

## Runtime & cost (observed)

| Step | First run | Re-run |
|---|---|---|
| Download (17.9 GB, chunked) | ~15–40 min (bandwidth) | skipped (manifest) |
| Load incl. 2B-edge filter scan | ~3 min | skipped (manifest) |
| dbt build (40 nodes) | ~11 s | ~11 s |
| LLM enrichment (150 domains) | ~5 min · ~$0.10–0.50 | $0 (cached) |

## Status

Build steps 1–4 (scaffold, extract, dbt, enrich) are complete; the
top-25 report, Omni semantic model, and scheduling stub land in steps
5–7 — tracked in [TECH_SPEC_DRAFT.md](TECH_SPEC_DRAFT.md) §9. This
README is finalized at wrap.
