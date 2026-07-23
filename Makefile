# Omni take-home — backlink gap-analysis pipeline.
# Quickstart: `make setup` then `make run`. See TECH_SPEC_DRAFT.md.

-include .env
export

.PHONY: setup init status extract transform enrich run test clean-db

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

status:     ## Show manifest progress and warehouse tables.
	uv run python -m pipeline status

run:        ## Run the full pipeline end to end (idempotent, resumable).
	uv run python -m pipeline run

test:       ## Run the test suite.
	uv run pytest -q

clean-db:   ## Delete the local warehouse file (downloads are kept).
	rm -f data/omni.duckdb data/omni.duckdb.wal
