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
**[TECH_SPEC.md](TECH_SPEC.md)**.

## Deliverables map

| Assignment deliverable | Where |
|---|---|
| ETL framework + code | [`pipeline/`](pipeline/) (Python: extract, transform, enrich stages + retry manifest) |
| dbt project | [`dbt/`](dbt/) (staging → intermediate → marts; tests + enforced contract) |
| Omni semantic model | [`omni/`](omni/) — view + topic in Omni's model-IDE layout, with an equivalent-SQL audit ([omni/README.md](omni/README.md)) |
| Top-25 report | [`artifacts/REPORT.md`](artifacts/REPORT.md) (human) + [`artifacts/top_25_report.csv`](artifacts/top_25_report.csv) (machine) |
| Tech Spec | [`TECH_SPEC.md`](TECH_SPEC.md) |

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
| `make report` | Regenerate `artifacts/` top-25 CSV + REPORT.md |
| `make reclassify` | Wipe the LLM cache + re-classify from scratch (~$0.15) |
| `make status` | Manifest progress + warehouse table counts |
| `make test` | Python unit tests (manifest, chunking, cache round-trip) |
| `make clean-db` | Drop the warehouse file (downloads are kept) |

Every command is idempotent — safe to re-run, safe to schedule.
(Direct CLI: `uv run python -m pipeline <init|status|extract|transform|enrich|reset|run>`.)

## Validating the system (reviewer checklist)

Ordered to mirror an actual review — from zero-setup reading to
adversarial poking.

**1. Read the deliverable (no setup)** —
[artifacts/REPORT.md](artifacts/REPORT.md): the top-25 with
per-domain rationale + suggested action, the auditable funnel, and
the deliberate-exclusions table. Every step below exists so you can
distrust-and-verify this file.

**2. Reproduce it byte-for-byte (no credentials)**

```bash
make setup && make run    # keyless: enrich runs as a loud DRY RUN
git status artifacts/     # clean = the committed report is exactly
                          # what the pipeline emits
```

Reproducibility pins: crawl release ID · `uv.lock` · pinned model ID
+ `temperature=0` + JSON-schema outputs · committed enrichment cache
with `model`/`enriched_at` provenance.

**3. Manually audit any report row** — every claim in REPORT.md is
one query away. Pick a domain and trace it end to end (mart row →
link evidence → gap proof → independent authority check → score
recomputation → LLM verdict):

```bash
DOMAIN=fivetran.com uv run python -c "
import os, duckdb
d = os.environ['DOMAIN']
con = duckdb.connect('data/omni.duckdb', read_only=True)
q = lambda sql: con.execute(sql, [d]).fetchall()
print('mart row :', q('''select competitor_consensus, harmonic_pos,
    round(opportunity_score, 3), category, opportunity_type
    from marts.top_backlink_opportunities where domain = ?'''))
print('links to :', q('''select list(distinct competitor)
    from intermediate.int_referring_domain_links
    where domain = ?'''))
print('gap proof:', q('''select not links_to_omni
    from intermediate.int_domain_signals where domain = ?'''))
print('raw rank :', q('''select ranks.harmonic_pos
    from raw.ranks as ranks
    join intermediate.int_domain_signals as signals
        using (domain_rev)
    where signals.domain = ?'''))
print('score recomputes:', q('''select round(
    0.5 * (1.0 / log10(harmonic_pos + 10))
    + 0.5 * (competitor_consensus / 4.0), 3)
    from marts.top_backlink_opportunities where domain = ?'''))
print('llm cache:', q('''select is_relevant, category, model
    from enrich.domain_enrichment where domain = ?'''))
"
```

The funnel numbers in REPORT.md are each a `count(*)` on the tables
named in [pipeline/report.py](pipeline/report.py). The LLM verdict
history is `git log -p artifacts/enrichment_cache.csv` (prompt
v1 → v2 → v2.1, every flip diffable), and human overrides live in
[dbt/seeds/enrichment_overrides.csv](dbt/seeds/enrichment_overrides.csv).

**4. Data tests & contracts** — these already ran inside `make run`;
rerun standalone with `make transform`: 49 dbt nodes green (3 seeds,
9 models, 37 tests), including the **thesis test** — no gap domain
links to Omni
(`dbt/tests/assert_no_gap_domain_links_to_omni.sql`) — and an
**enforced 12-column contract** on `top_backlink_opportunities`
(schema drift fails the build).

**5. Attack retry & recovery (spec B9)** — kill any stage mid-flight
(`Ctrl-C` during the download is the dramatic one), then `make run`:
the manifest resumes at the first incomplete unit. Inspect with
`make status`; force a redo with
`uv run python -m pipeline reset <stage>`.

**6. Unit tests** — `make test`: manifest claim/resume semantics,
download chunk planning, enrichment-cache round-trip.

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
omni/                Omni semantic model (view + topic + audit README)
artifacts/           committed pipeline outputs (enrichment cache, report)
data/                gitignored: 17.9 GB downloads + omni.duckdb warehouse
.github/workflows/   gated monthly cron for the recurring run
Makefile             the operator interface
TECH_SPEC.md         decision log + contracts + tradeoffs + recovery semantics
```

## Scheduling (the recurring-pipeline story)

Every command is idempotent and manifest-checkpointed, so
"scheduled" simply means "re-invoked": a failed run needs no special
recovery — the next invocation resumes at the first incomplete unit.

The committed [GitHub Actions workflow](.github/workflows/pipeline.yml)
runs monthly (CC webgraph cadence). The schedule is **gated behind
the repo variable `PIPELINE_SCHEDULE_ENABLED`** — deliberately,
because the 18 GB download exceeds GitHub-hosted runner disk; enable
it on a self-hosted runner or with the MotherDuck `prod` target
([dbt/profiles.yml](dbt/profiles.yml)). Manual runs:
Actions → backlink-pipeline → *Run workflow* (works keyless via the
DRY RUN path). Locally, any scheduler that can invoke `make run`
works as-is.

## Runtime & cost (observed)

| Step | First run | Re-run |
|---|---|---|
| Download (17.9 GB, chunked) | ~15–40 min (bandwidth) | skipped (manifest) |
| Load incl. 2B-edge filter scan | ~3 min | skipped (manifest) |
| dbt build (40 nodes) | ~11 s | ~11 s |
| LLM enrichment (150 domains) | ~5 min · ~$0.10–0.50 | $0 (cached) |

## Status

**Complete.** All seven build steps and all six brief deliverables
are shipped; the full build log — including the LLM prompt
iteration story (v1 → v2 → v2.1, regression gate, human overrides)
— is in [TECH_SPEC.md](TECH_SPEC.md) §9; deliverables in §12,
if-I-had-a-week priorities in §10, out of scope in §11.
