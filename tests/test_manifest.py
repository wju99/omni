"""Tests for the pipeline-manifest retry/recovery helpers (spec B9)."""

from pipeline import db


def _connect(tmp_path):
    return db.connect(tmp_path / "test.duckdb")


def test_claim_and_done_lifecycle(tmp_path):
    con = _connect(tmp_path)
    assert db.claim(con, "download", "edges") is True
    db.mark_done(con, "download", "edges", detail="14.6 GB")
    # Completed units are not re-claimed on re-run (resume semantics).
    assert db.claim(con, "download", "edges") is False


def test_failed_units_are_retryable_and_attempts_increment(tmp_path):
    con = _connect(tmp_path)
    assert db.claim(con, "enrich", "example.com") is True
    db.mark_failed(con, "enrich", "example.com", "rate limited")
    assert db.claim(con, "enrich", "example.com") is True
    row = con.execute(
        "SELECT status, attempts FROM pipeline_manifest "
        "WHERE stage = 'enrich' AND unit = 'example.com'"
    ).fetchone()
    assert row == ("in_progress", 2)


def test_units_and_stages_are_independent(tmp_path):
    con = _connect(tmp_path)
    db.claim(con, "download", "edges")
    db.mark_done(con, "download", "edges")
    assert db.claim(con, "download", "vertices") is True
    assert db.claim(con, "enrich", "edges") is True
