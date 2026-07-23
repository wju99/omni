"""Tests for extract chunk planning (download resume units)."""

from pipeline import extract


def test_chunk_plan_partial_last_chunk():
    assert extract.chunk_plan(100, 30) == [
        (0, 0, 29), (1, 30, 59), (2, 60, 89), (3, 90, 99)]


def test_chunk_plan_exact_multiple():
    assert extract.chunk_plan(60, 30) == [(0, 0, 29), (1, 30, 59)]


def test_chunk_plan_single_small_chunk():
    assert extract.chunk_plan(5, 30) == [(0, 0, 4)]


def test_chunk_plan_covers_file_exactly():
    total = 14_599_083_459  # Real edges file size (spec §3).
    plan = extract.chunk_plan(total)
    assert plan[0][1] == 0
    assert plan[-1][2] == total - 1
    covered = sum(end - start + 1 for _, start, end in plan)
    assert covered == total


def test_downloaded_bytes_counts_only_done_chunks(tmp_path):
    from pipeline import db
    con = db.connect(tmp_path / "t.duckdb")
    db.claim(con, "download", "vertices:00000")
    db.mark_done(con, "download", "vertices:00000", detail="100")
    db.claim(con, "download", "vertices:00001")
    db.mark_done(con, "download", "vertices:00001", detail="50")
    db.claim(con, "download", "vertices:00002")  # in_progress
    db.claim(con, "download", "edges:00000")
    db.mark_done(con, "download", "edges:00000", detail="999")
    assert extract._downloaded_bytes(con, "vertices") == 150
    assert extract._downloaded_bytes(con, "edges") == 999
    assert extract._downloaded_bytes(con, "ranks") == 0
    con.close()
