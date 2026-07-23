"""Report stage: publish the top-25 deliverable (spec B13).

Writes two committed artifacts from the contracted mart:
  artifacts/top_25_report.csv — machine-readable, stable columns
  artifacts/REPORT.md         — the Growth-Marketing-facing report

Deterministic by design: all content derives from warehouse tables
and pinned config — no wall-clock timestamps — so re-runs on the
same data are byte-identical (see README, "Validating the system").
"""

import csv

from pipeline import config
from pipeline import db

_CSV_PATH = config.ARTIFACTS_DIR / "top_25_report.csv"
_MD_PATH = config.ARTIFACTS_DIR / "REPORT.md"

# Deterministic outreach playbook keyed by opportunity_type: the LLM
# picks the type; the action wording is ours, so outreach advice is
# stable and editable without re-classifying anything.
_ACTIONS = {
    "integrations_page": (
        "Pitch Omni for their integrations/destinations directory; "
        "offer a co-marketing blurb or joint documentation."),
    "comparison_or_alternatives": (
        "Request inclusion in their BI comparison / alternatives "
        "content."),
    "guest_content": (
        "Pitch a guest post or technical tutorial featuring Omni."),
    "directory_listing": (
        "Submit a complete Omni listing to the directory."),
    "partner_program": (
        "Apply to the partner program; the backlink ships with the "
        "listing."),
    "content_mention": (
        "Pitch a briefing or story angle; aim for a linked product "
        "mention."),
    "not_applicable": "Review manually.",
}

_TOP_SQL = """
    select
        domain,
        competitor_consensus,
        links_to_sigma,
        links_to_hex,
        links_to_mode,
        links_to_metabase,
        harmonic_pos,
        pagerank_pos,
        opportunity_score,
        category,
        opportunity_type,
        rationale
    from marts.top_backlink_opportunities
    order by opportunity_score desc, domain
"""

_FOOTPRINT_SQL = """
    select competitor, count(distinct domain) as referring_domains
    from intermediate.int_referring_domain_links
    group by 1
    order by 2 desc
"""

_FUNNEL_SQL = """
    select
        (select count(*) from raw.vertices) as webgraph_domains,
        (select count(*) from intermediate.int_domain_signals)
            as linking_any_target,
        (select count(*) from intermediate.int_domain_signals
            where not links_to_omni and competitor_consensus >= 1)
            as raw_gap,
        (select count(*) from marts.backlink_opportunities)
            as after_filters,
        (select count(*) from marts.enrichment_shortlist)
            as shortlisted,
        (select count(*)
            from enrich.domain_enrichment as llm
            left join seeds.enrichment_overrides as overrides
                on llm.domain = overrides.domain
            where coalesce(overrides.is_relevant, llm.is_relevant))
            as judged_relevant,
        (select count(*) from marts.top_backlink_opportunities)
            as final_recommendations
"""

# High-authority gap domains the relevance gate cut — the "insights
# beyond the 25" evidence (deliberate exclusions, with reasons).
_EXCLUSIONS_SQL = """
    select
        opportunities.domain,
        opportunities.harmonic_pos,
        enrichment.category,
        enrichment.rationale
    from marts.backlink_opportunities as opportunities
    inner join enrich.domain_enrichment as enrichment
        on opportunities.domain = enrichment.domain
    left join seeds.enrichment_overrides as overrides
        on opportunities.domain = overrides.domain
    where not coalesce(overrides.is_relevant,
                       enrichment.is_relevant)
    order by opportunities.harmonic_pos asc, opportunities.domain
    limit 6
"""


def _md_escape(text: str) -> str:
    """Escapes pipe characters so LLM text cannot break md tables."""
    return str(text).replace("|", "\\|")


def _action_for(opportunity_type: str) -> str:
    """Returns the playbook action for an opportunity type."""
    return _ACTIONS.get(opportunity_type, _ACTIONS["not_applicable"])


def _write_csv(rows) -> None:
    """Writes the machine-readable artifact (stable column order)."""
    _CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    header = ("rank", "domain", "competitor_consensus",
              "links_to_sigma", "links_to_hex", "links_to_mode",
              "links_to_metabase", "harmonic_pos", "pagerank_pos",
              "opportunity_score", "category", "opportunity_type",
              "rationale", "suggested_action")
    with open(_CSV_PATH, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for rank, row in enumerate(rows, start=1):
            writer.writerow(
                (rank,) + tuple(row) + (_action_for(row[10]),))


def _render_md(top, footprint, funnel, exclusions) -> str:
    """Renders REPORT.md from query results (pure function)."""
    lines = []
    out = lines.append
    out("# Omni Backlink Gap Analysis — Top 25 Opportunities")
    out("")
    out(f"**Data:** Common Crawl domain webgraph `{config.RELEASE}`"
        f" (aggregating `{config.CRAWL_INPUTS[0]}`, May 8–21, and"
        f" `{config.CRAWL_INPUTS[1]}`, Jun 5–18, 2026).")
    out(f"**Relevance labels:** `{config.ANTHROPIC_MODEL}`,"
        " temperature 0, JSON-schema outputs — cached and committed"
        " in `enrichment_cache.csv` (no API key needed to"
        " reproduce).")
    out("")

    out("## Why this matters")
    out("")
    out("| Company | Referring domains |")
    out("|---|---|")
    counts = dict(footprint)
    for competitor, n in footprint:
        marker = " ← **Omni**" if competitor == config.OMNI_KEY \
            else ""
        out(f"| {competitor} | {n:,}{marker} |")
    out("")
    if config.OMNI_KEY in counts and footprint:
        leader, leader_n = footprint[0]
        omni_n = counts[config.OMNI_KEY]
        if leader != config.OMNI_KEY and omni_n:
            out(f"Omni's backlink footprint is **{omni_n:,} referring"
                f" domains — about 1/{round(leader_n / omni_n)} of"
                f" {leader}'s {leader_n:,}**. Every row below is a"
                " domain that already links to competitors (so the"
                " topic fit is proven) but not to Omni.")
            out("")

    out("## How this list was built")
    out("")
    w, a, g, f, s, r, t = funnel
    out(f"1. **{w:,}** domains in the webgraph")
    out(f"2. **{a:,}** link to at least one of the five tracked"
        " companies")
    out(f"3. **{g:,}** link to a competitor but **not** to Omni"
        " (the gap)")
    out(f"4. **{f:,}** after deterministic filters (junk TLDs,"
        " platform wildcards, mega-platforms, authority floor)")
    out(f"5. **{s:,}** shortlisted by consensus × authority score")
    out(f"6. **{r:,}** judged relevant outreach targets (LLM"
        " relevance gate + human-verified overrides)")
    out(f"7. **{t:,}** final recommendations below")
    out("")
    out("**Score** = weighted blend of *competitor consensus* (how"
        " many of the four competitors the domain links to) and"
        " *authority* (Common Crawl harmonic-centrality rank)."
        " The LLM contributes only relevance/category labels —"
        " never the ranking.")
    out("")

    out("## The 25 recommendations")
    out("")
    if not top:
        out("_No classified opportunities yet — run the enrich"
            " stage (see README)._")
        out("")
    else:
        out("| # | Domain | Why it matters | Suggested action |"
            " Consensus | Authority rank | Score |")
        out("|---|---|---|---|---|---|---|")
        for rank, row in enumerate(top, start=1):
            (domain, consensus, _s, _h, _m, _b, harmonic_pos,
             _pagerank, score, _category, opportunity_type,
             rationale) = row
            out(f"| {rank} | **{domain}** |"
                f" {_md_escape(rationale)} |"
                f" {_action_for(opportunity_type)} |"
                f" {consensus}/4 | {harmonic_pos:,} |"
                f" {score:.3f} |")
        out("")

    out("## Notable deliberate exclusions")
    out("")
    out("High-authority domains in the gap that were **cut on"
        " actionability** — a reminder that this list optimizes for"
        " *outreach you can actually do*, not raw authority:")
    out("")
    out("| Domain | Authority rank | Category | Reason |")
    out("|---|---|---|---|")
    for domain, harmonic_pos, category, rationale in exclusions:
        out(f"| {domain} | {harmonic_pos:,} | {category} |"
            f" {_md_escape(rationale)} |")
    out("")

    out("## Insights beyond the list")
    out("")
    out("- **Competitors earn links Omni cannot pitch for** —"
        " comparison/\"vs\" pages on other vendors' sites and"
        " organic community links (e.g. Hacker News at domain"
        " grain). The counter-move is content, not outreach: build"
        " Omni's own comparison pages targeting those keywords.")
    out("- **The integrations-directory motion dominates** the"
        " list: most recommendations are data-stack vendors whose"
        " directories already list BI tools. A single partner-page"
        " template + outreach sequence covers most of the 25.")
    out("- **Entity duplicates exist at domain grain** (e.g."
        " montecarlo.ai vs montecarlodata.com) — treat them as one"
        " outreach target.")
    out("")

    out("## Known limitations")
    out("")
    out("- Classification is **name + link-signal based** (no page"
        " fetch at MVP); a future upgrade grounds the LLM with"
        " homepage titles/descriptions.")
    out("- The LLM competitor rule was violated in 2 of 150"
        " classifications despite an explicit closed list"
        " (98.7% compliance) — documented in the Tech Spec;"
        " human review of 25 rows is the backstop.")
    out("- Link *presence* comes from the crawl window; a link"
        " dropped after June 2026 may persist until the next"
        " release refresh.")
    out("")

    out("## Reproduce")
    out("")
    out("`make setup && make run` — no API key required; see"
        " [README](../README.md). Data and classifications are"
        " pinned; re-runs are byte-identical.")
    out("")
    return "\n".join(lines)


def run() -> None:
    """Generates both report artifacts from the warehouse."""
    con = db.connect()
    try:
        top = con.execute(_TOP_SQL).fetchall()
        footprint = con.execute(_FOOTPRINT_SQL).fetchall()
        funnel = con.execute(_FUNNEL_SQL).fetchone()
        exclusions = con.execute(_EXCLUSIONS_SQL).fetchall()
    finally:
        con.close()
    _write_csv(top)
    _MD_PATH.write_text(
        _render_md(top, footprint, funnel, exclusions))
    print(f"[report] wrote artifacts/top_25_report.csv "
          f"({len(top)} rows) and artifacts/REPORT.md")
