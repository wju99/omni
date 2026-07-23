"""DuckDB bootstrap plus pipeline-manifest retry/recovery helpers.

The manifest is the pipeline's recovery backbone (spec B9). Work at
the two flaky external seams (webgraph downloads, LLM enrichment
calls) is split into units keyed by (release, stage, unit): a unit is
claimed before work starts, marked done on success, and marked failed
(but re-claimable) on error. Re-runs skip done units, so an
interrupted run resumes where it stopped. This is single-process
resume bookkeeping — a deliberate MVP-scale mirror of the team's
concurrent "claim a row" pattern, not a distributed lock (DuckDB is a
single-writer store).
"""

import pathlib

import duckdb

from pipeline import config

_SCHEMAS = ("raw", "enrich")

_MANIFEST_DDL = """
CREATE TABLE IF NOT EXISTS pipeline_manifest (
    release    VARCHAR NOT NULL,
    stage      VARCHAR NOT NULL,
    unit       VARCHAR NOT NULL,
    status     VARCHAR NOT NULL,
    attempts   INTEGER NOT NULL DEFAULT 0,
    detail     VARCHAR,
    updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (release, stage, unit)
)
"""

# LLM enrichment cache (spec B8): written by the enrich stage,
# declared as a dbt *source*. Created empty at init so dbt builds
# succeed before any enrichment has run (mirrors the team's
# "LLM enrichment -> raw outputs -> dbt" pattern).
_ENRICHMENT_DDL = """
CREATE TABLE IF NOT EXISTS enrich.domain_enrichment (
    domain           VARCHAR PRIMARY KEY,
    is_relevant      BOOLEAN,
    category         VARCHAR,
    opportunity_type VARCHAR,
    rationale        VARCHAR,
    model            VARCHAR,
    enriched_at      TIMESTAMP DEFAULT current_timestamp
)
"""


def connect(db_path=None) -> duckdb.DuckDBPyConnection:
    """Opens (and initializes) the DuckDB warehouse.

    Args:
        db_path: Optional override of config.DB_PATH (used by tests).

    Returns:
        An open DuckDB connection with schemas and manifest ensured.
    """
    path = pathlib.Path(db_path) if db_path else config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        con = duckdb.connect(str(path))
    except duckdb.IOException as error:
        raise SystemExit(
            "warehouse is locked — another pipeline process (e.g. a "
            "running extract) holds it; wait for it to finish and "
            f"re-run. ({error})"
        ) from error
    init_db(con)
    return con


def init_db(con: duckdb.DuckDBPyConnection) -> None:
    """Creates schemas, the manifest, and the enrichment cache."""
    for schema in _SCHEMAS:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    con.execute(_MANIFEST_DDL)
    con.execute(_ENRICHMENT_DDL)


def claim(con, stage: str, unit: str, release: str = None) -> bool:
    """Claims a unit of work unless it has already completed.

    Args:
        con: Open warehouse connection.
        stage: Pipeline stage name (e.g. 'download', 'enrich').
        unit: Stage-specific unit id (file name, chunk id, domain).
        release: Webgraph release; defaults to config.RELEASE.

    Returns:
        True if the caller should do the work; False if the unit is
        already done and must be skipped (resume semantics).
    """
    release = release or config.RELEASE
    row = con.execute(
        "SELECT status FROM pipeline_manifest "
        "WHERE release = ? AND stage = ? AND unit = ?",
        [release, stage, unit],
    ).fetchone()
    if row and row[0] == "done":
        return False
    con.execute(
        """
        INSERT INTO pipeline_manifest
            (release, stage, unit, status, attempts)
        VALUES (?, ?, ?, 'in_progress', 1)
        ON CONFLICT (release, stage, unit) DO UPDATE SET
            status = 'in_progress',
            attempts = attempts + 1,
            updated_at = now()
        """,
        [release, stage, unit],
    )
    return True


def mark_done(con, stage: str, unit: str, detail: str = None,
              release: str = None) -> None:
    """Marks a claimed unit as completed."""
    _set_status(con, stage, unit, "done", detail, release)


def mark_failed(con, stage: str, unit: str, error,
                release: str = None) -> None:
    """Marks a claimed unit as failed; it stays re-claimable."""
    _set_status(con, stage, unit, "failed", str(error)[:500], release)


def _set_status(con, stage, unit, status, detail, release) -> None:
    con.execute(
        "UPDATE pipeline_manifest SET status = ?, detail = ?, "
        "updated_at = now() "
        "WHERE release = ? AND stage = ? AND unit = ?",
        [status, detail, release or config.RELEASE, stage, unit],
    )


def status_summary(con):
    """Returns (stage, status, units, max_attempts, last_update) rows."""
    return con.execute(
        "SELECT stage, status, count(*), max(attempts), "
        "max(updated_at) FROM pipeline_manifest "
        "GROUP BY 1, 2 ORDER BY 1, 2"
    ).fetchall()


def table_summary(con):
    """Returns (schema, table, row_count) for all user tables."""
    tables = con.execute(
        "SELECT schema_name, table_name FROM duckdb_tables() "
        "ORDER BY schema_name, table_name"
    ).fetchall()
    out = []
    for schema, table in tables:
        count = con.execute(
            f'SELECT count(*) FROM "{schema}"."{table}"'
        ).fetchone()[0]
        out.append((schema, table, count))
    return out
