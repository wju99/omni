"""Tests for the report stage's deterministic pieces."""

from pipeline import enrich
from pipeline import report


def test_every_opportunity_type_has_an_action():
    # The playbook must stay in lockstep with the LLM's enum.
    assert set(report._ACTIONS) == set(enrich._OPPORTUNITY_TYPES)


def test_unknown_opportunity_type_falls_back_safely():
    assert report._action_for("???") == "Review manually."


def test_md_escape_neutralizes_table_breakage():
    assert report._md_escape("a|b") == "a\\|b"


def test_render_md_handles_empty_top_list():
    text = report._render_md(
        top=[],
        footprint=[("metabase", 1809), ("omni", 265)],
        funnel=(100, 50, 40, 30, 20, 10, 0),
        exclusions=[],
    )
    assert "No classified opportunities yet" in text
    assert "1/7 of metabase" in text
