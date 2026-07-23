# Omni take-home — backlink gap-analysis pipeline.
# Quickstart: `make setup` then `make run`. See TECH_SPEC_DRAFT.md.

-include .env
export

.PHONY: setup init status extract transform enrich reclassify report run test clean-db

setup:      ## Install pinned dependencies into .venv (requires uv).
	uv sync

init:       ## Create the DuckDB warehouse, schemas, and manifest.
	uv run python -m pipeline init

extract:    ## Download webgraph + load raw tables (resumable).
	uv run python -m pipeline extract

transform:  ## Build + test all dbt models (seeds, models, tests).
	uv run python -m pipeline transform

enrich:     ## Classify shortlist with Claude (DRY RUN without key).
	uv run python -m pipeline enrich

reclassify: ## Wipe the LLM cache and re-classify from scratch (~$0.15).
	rm -f artifacts/enrichment_cache.csv
	uv run python -m pipeline reset enrich
	uv run python -c "from pipeline import db; \
	con = db.connect(); \
	con.execute('DELETE FROM enrich.domain_enrichment'); \
	con.close(); print('enrichment cache table wiped')"
	uv run python -m pipeline enrich

report:     ## Write top-25 CSV + Markdown artifacts.
	uv run python -m pipeline report

status:     ## Show manifest progress and warehouse tables.
	uv run python -m pipeline status

run:        ## Run the full pipeline end to end (idempotent, resumable).
	uv run python -m pipeline run

test:       ## Run the test suite.
	uv run pytest -q

clean-db:   ## Delete the local warehouse file (downloads are kept).
	rm -f data/omni.duckdb data/omni.duckdb.wal
