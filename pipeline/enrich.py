"""Enrich stage: bounded, cached LLM classification (spec B8).

Reads the deterministic shortlist mart, classifies each domain with
Claude Haiku 4.5 via structured outputs (a JSON-schema-enforced
response shape — the explicit contract with the LLM), and upserts
results into ``enrich.domain_enrichment`` keyed by domain.

The cache table is this stage's checkpoint (spec B9), and — exported
to the committed ``artifacts/enrichment_cache.csv`` — its
reproducibility snapshot: a reviewer with no API key re-runs the
whole pipeline from the committed classifications.

Without ``ANTHROPIC_API_KEY`` the stage is an explicit DRY RUN: it
bootstraps the cache from the committed CSV, makes zero API calls,
and says so loudly.
"""

import json
import os

import anthropic

from pipeline import config
from pipeline import db

_CACHE_CSV = config.ARTIFACTS_DIR / "enrichment_cache.csv"

# Column order matches the enrich.domain_enrichment DDL and the
# committed CSV header (an explicit repo-artifact contract).
_CACHE_COLUMNS = ("domain", "is_relevant", "category",
                  "opportunity_type", "rationale", "model",
                  "enriched_at")

_CATEGORIES = (
    "data_platform_vendor",
    "developer_tool_vendor",
    "tech_media_or_blog",
    "community_or_directory",
    "education_or_research",
    "consultancy_or_agency",
    "aggregator_or_listicle",
    "junk_or_spam",
    "other",
)

_OPPORTUNITY_TYPES = (
    "integrations_page",
    "comparison_or_alternatives",
    "guest_content",
    "directory_listing",
    "partner_program",
    "content_mention",
    "not_applicable",
)

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "is_relevant": {"type": "boolean"},
        "category": {"type": "string", "enum": list(_CATEGORIES)},
        "opportunity_type": {
            "type": "string",
            "enum": list(_OPPORTUNITY_TYPES),
        },
        "rationale": {"type": "string"},
    },
    "required": [
        "is_relevant", "category", "opportunity_type", "rationale",
    ],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = (
    "You are a growth-marketing analyst for Omni (omni.co), a "
    "business-intelligence and analytics platform. You evaluate "
    "referring domains — domains that link to Omni's competitors "
    "(Sigma, Hex, Mode, Metabase) but not to Omni — as potential "
    "backlink-outreach targets.\n"
    "Classify from the domain name, the link signals provided, and "
    "your knowledge of the data/analytics ecosystem. Be decisive.\n"
    "- is_relevant: true only if outreach could plausibly yield a "
    "valuable, on-topic backlink (data/analytics/BI vendors and "
    "blogs, credible tech media, tool directories, education, "
    "consultancies). false for spam, link farms, generic listicle "
    "mills, and off-topic or unidentifiable domains.\n"
    "- category and opportunity_type: pick the single best value.\n"
    "- rationale: one crisp sentence (max 25 words) a marketer can "
    "act on."
)


def _bootstrap_cache(con, csv_path=_CACHE_CSV) -> int:
    """Loads the committed cache CSV if the cache table is empty.

    Args:
        con: Open warehouse connection.
        csv_path: Committed cache CSV; missing file is a no-op.

    Returns:
        Number of rows loaded (0 if table was non-empty or no CSV).
    """
    count = con.execute(
        "SELECT count(*) FROM enrich.domain_enrichment"
    ).fetchone()[0]
    if count or not csv_path.is_file():
        return 0
    con.execute(
        "INSERT INTO enrich.domain_enrichment "
        f"SELECT * FROM read_csv('{csv_path}', header=true)")
    return con.execute(
        "SELECT count(*) FROM enrich.domain_enrichment"
    ).fetchone()[0]


def _export_cache(con, csv_path=_CACHE_CSV) -> int:
    """Writes the cache table to the committed CSV (stable order).

    Args:
        con: Open warehouse connection.
        csv_path: Destination CSV path.

    Returns:
        Number of rows exported.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    columns = ", ".join(_CACHE_COLUMNS)
    con.execute(
        f"COPY (SELECT {columns} FROM enrich.domain_enrichment "
        f"ORDER BY domain) TO '{csv_path}' (HEADER)")
    return con.execute(
        "SELECT count(*) FROM enrich.domain_enrichment"
    ).fetchone()[0]


def _uncached_shortlist(con):
    """Returns shortlist rows lacking a cache entry, best first."""
    return con.execute("""
        SELECT
            shortlist.domain,
            opportunities.competitor_consensus,
            opportunities.harmonic_pos,
            opportunities.links_to_sigma,
            opportunities.links_to_hex,
            opportunities.links_to_mode,
            opportunities.links_to_metabase
        FROM marts.enrichment_shortlist AS shortlist
        INNER JOIN marts.backlink_opportunities AS opportunities
            ON shortlist.domain = opportunities.domain
        WHERE shortlist.domain NOT IN (
            SELECT domain FROM enrich.domain_enrichment)
        ORDER BY shortlist.opportunity_score DESC
    """).fetchall()


def _classify(client, row) -> dict:
    """Calls Haiku once for one domain; returns parsed labels.

    Args:
        client: anthropic.Anthropic client (SDK handles backoff).
        row: One _uncached_shortlist row.

    Returns:
        Dict matching _RESPONSE_SCHEMA (API-enforced).
    """
    (domain, consensus, harmonic_pos, links_sigma, links_hex,
     links_mode, links_metabase) = row
    linked = [name for name, flag in (
        ("sigma", links_sigma), ("hex", links_hex),
        ("mode", links_mode), ("metabase", links_metabase)) if flag]
    prompt = (
        f"Domain: {domain}\n"
        f"Links to competitors: {', '.join(linked)}\n"
        f"Competitor consensus: {consensus} of 4\n"
        f"Common Crawl harmonic-centrality rank: {harmonic_pos:,} "
        "(lower = more authoritative; ~121M domains ranked)\n\n"
        "Classify this domain as a backlink opportunity for Omni."
    )
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=500,
        temperature=0,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": _RESPONSE_SCHEMA,
            },
        },
    )
    text = next(block.text for block in response.content
                if block.type == "text")
    return json.loads(text)


def _store(con, domain: str, labels: dict) -> None:
    """Upserts one classification (with provenance) into the cache."""
    con.execute(
        "INSERT OR REPLACE INTO enrich.domain_enrichment "
        "(domain, is_relevant, category, opportunity_type, "
        "rationale, model, enriched_at) "
        "VALUES (?, ?, ?, ?, ?, ?, now())",
        [domain, labels["is_relevant"], labels["category"],
         labels["opportunity_type"], labels["rationale"],
         config.ANTHROPIC_MODEL])


def _print_dry_run_banner(cached: int, uncached: int) -> None:
    """Prints the explicit keyless DRY RUN notice."""
    bar = "=" * 64
    print(bar)
    print("[enrich] DRY RUN — ANTHROPIC_API_KEY is not set")
    print("[enrich] No LLM calls will be made; no cost incurred.")
    print("[enrich] Using the committed enrichment cache only: "
          f"artifacts/enrichment_cache.csv ({cached} rows)")
    print(f"[enrich] Shortlist domains without a cache entry: "
          f"{uncached} (skipped this run)")
    print("[enrich] Set ANTHROPIC_API_KEY in .env to classify "
          "them.")
    print(bar, flush=True)


def run() -> None:
    """Runs the enrich stage (dry-run aware, resumable, cached)."""
    con = db.connect()
    try:
        loaded = _bootstrap_cache(con)
        if loaded:
            print(f"[enrich] bootstrapped cache from committed "
                  f"CSV: {loaded} rows")
        pending = _uncached_shortlist(con)
        if not os.environ.get("ANTHROPIC_API_KEY"):
            cached = con.execute(
                "SELECT count(*) FROM enrich.domain_enrichment"
            ).fetchone()[0]
            _print_dry_run_banner(cached, len(pending))
            return
        if not pending:
            print("[enrich] cache complete — nothing to classify")
            return
        print(f"[enrich] live mode: classifying {len(pending)} "
              f"domains with {config.ANTHROPIC_MODEL}", flush=True)
        client = anthropic.Anthropic(max_retries=5)
        failures = 0
        for index, row in enumerate(pending, start=1):
            domain = row[0]
            if not db.claim(con, "enrich", domain):
                continue
            try:
                labels = _classify(client, row)
            except Exception as error:  # Flaky seam (spec B9).
                db.mark_failed(con, "enrich", domain, error)
                failures += 1
                print(f"[enrich] {domain}: FAILED ({error})",
                      flush=True)
                continue
            _store(con, domain, labels)
            db.mark_done(con, "enrich", domain,
                         detail=labels["category"])
            print(f"[enrich] {index}/{len(pending)} {domain}: "
                  f"relevant={labels['is_relevant']} "
                  f"{labels['category']}", flush=True)
        exported = _export_cache(con)
        print(f"[enrich] cache exported to "
              f"artifacts/enrichment_cache.csv ({exported} rows)")
        if failures:
            print(f"[enrich] {failures} domains failed after SDK "
                  "retries; re-run to retry (manifest tracks them)")
    finally:
        con.close()
