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
