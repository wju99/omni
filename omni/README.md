# Omni semantic model

The semantic-layer deliverable: a hand-authored Omni **view** +
**topic** over the pipeline's contracted `marts.top_backlink_opportunities`
table, written in the same file layout Omni's model IDE uses
(`views/*.view`, `topics/*.topic`).

```
omni/
├── views/top_backlink_opportunities.view   fields: dimensions + measures
└── topics/backlink_opportunities.topic     curated query starting point
```

## How this maps to Omni's three-layer model

| Omni layer | In this project |
|---|---|
| **Schema model** (auto-generated from the warehouse) | Omni would introspect `marts.*` — clean mart naming means the generated baseline is already right |
| **Shared model** (governed curation) | **These files**: labels, groups, derived fields (`tld`, `authority_bucket`), measures, a filtered measure, AI context |
| **Workbook model** (ad-hoc) | Where Growth would explore the topic and promote refinements back up |

## How it would connect (not run locally)

Hosted Omni cannot reach a laptop DuckDB file. The documented path
(spec B15): switch dbt to the `prod` MotherDuck target
(`dbt/profiles.yml`, one line), then point an Omni connection at the
same MotherDuck database. Omni generates its schema model from
`marts`, and these files apply on top. **Stretch (validation B):**
free Omni instance + MotherDuck import with screenshots.

## How to validate without a live Omni instance (validation A)

1. **The data is already machine-validated** — the mart these files
   sit on is dbt-built with an enforced 12-column contract and
   tests (uniqueness, the no-gap-links-to-Omni thesis test, cap).
   The semantic layer only adds meaning; the numbers are proven
   upstream.
2. **Syntax is grounded in Omni's docs, not memory** — every
   parameter used appears in Omni's parameter references:
   [views](https://docs.omni.co/modeling/views/parameters),
   [dimensions](https://docs.omni.co/modeling/dimensions)
   (`primary_key`, `group_label`, `sql`, `format`),
   [measures](https://docs.omni.co/modeling/measures)
   (`aggregate_type`, filtered measures),
   [topics](https://docs.omni.co/modeling/topics/parameters)
   (`base_view`, `default_row_limit`, `ai_context`).
3. **Equivalent-SQL audit** — every measure has a direct DuckDB
   translation a reviewer can run against `data/omni.duckdb`:

| Omni measure | Equivalent SQL over `marts.top_backlink_opportunities` |
|---|---|
| `opportunity_count` | `select count(*) from …` |
| `avg_opportunity_score` | `select avg(opportunity_score) from …` |
| `avg_consensus` | `select avg(competitor_consensus) from …` |
| `best_authority_rank` | `select min(harmonic_pos) from …` |
| `integrations_page_count` | `select count(*) from … where opportunity_type = 'integrations_page'` |
| dim `tld` | `select regexp_extract(domain, '([^.]+)$') from …` |
| dim `authority_bucket` | the `CASE` expression in the view file, verbatim |

## Design notes

- **One topic, one view — deliberately** (spec B12): a 25-row wide
  mart is a degenerate star; more files would add surface area for
  format errors, not value. Week-1: a second topic over the full
  3,008-row gap set with a join for drill-down.
- `ai_context` on both files targets Omni's AI/agent features —
  the topic is phrased for the questions Growth would actually ask.
- The ranking is deterministic (consensus × authority); the LLM
  gates relevance only. `rationale` is exposed as a dimension so
  every row explains itself in the UI.
