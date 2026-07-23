"""Tests for the enrichment cache round-trip (keyless repro path)."""

from pipeline import db
from pipeline import enrich

_LABELS = {
    "is_relevant": True,
    "category": "data_platform_vendor",
    "opportunity_type": "integrations_page",
    "rationale": "ELT vendor; integrations page lists BI tools.",
}


def test_cache_export_and_bootstrap_roundtrip(tmp_path):
    csv_path = tmp_path / "cache.csv"
    con = db.connect(tmp_path / "a.duckdb")
    enrich._store(con, "fivetran.com", _LABELS)
    assert enrich._export_cache(con, csv_path) == 1
    con.close()

    # A fresh warehouse (reviewer machine) bootstraps from the CSV.
    fresh = db.connect(tmp_path / "b.duckdb")
    assert enrich._bootstrap_cache(fresh, csv_path) == 1
    row = fresh.execute(
        "SELECT domain, is_relevant, category "
        "FROM enrich.domain_enrichment").fetchone()
    assert row == ("fivetran.com", True, "data_platform_vendor")
    fresh.close()


def test_bootstrap_is_noop_when_cache_populated(tmp_path):
    csv_path = tmp_path / "cache.csv"
    con = db.connect(tmp_path / "a.duckdb")
    enrich._store(con, "fivetran.com", _LABELS)
    enrich._export_cache(con, csv_path)
    # Table already has rows -> bootstrap must not double-load.
    assert enrich._bootstrap_cache(con, csv_path) == 0
    con.close()


def test_bootstrap_is_noop_without_csv(tmp_path):
    con = db.connect(tmp_path / "a.duckdb")
    assert enrich._bootstrap_cache(con, tmp_path / "nope.csv") == 0
    con.close()


def test_response_schema_is_strict():
    schema = enrich._RESPONSE_SCHEMA
    assert set(schema["required"]) == set(schema["properties"])
    assert schema["additionalProperties"] is False
