# Omni Backlink Gap Analysis — Top 25 Opportunities

**Data:** Common Crawl domain webgraph `cc-main-2026-apr-may-jun` (aggregating `CC-MAIN-2026-21`, May 8–21, and `CC-MAIN-2026-25`, Jun 5–18, 2026).
**Relevance labels:** `claude-haiku-4-5`, temperature 0, JSON-schema outputs — cached and committed in `enrichment_cache.csv` (no API key needed to reproduce).

## Why this matters

| Company | Referring domains |
|---|---|
| metabase | 1,809 |
| mode | 1,242 |
| hex | 838 |
| sigma | 738 |
| omni | 265 ← **Omni** |

Omni's backlink footprint is **265 referring domains — about 1/7 of metabase's 1,809**. Every row below is a domain that already links to competitors (so the topic fit is proven) but not to Omni.

## How this list was built

1. **121,091,933** domains in the webgraph
2. **4,023** link to at least one of the five tracked companies
3. **3,758** link to a competitor but **not** to Omni (the gap)
4. **3,008** after deterministic filters (junk TLDs, platform wildcards, mega-platforms, authority floor)
5. **150** shortlisted by consensus × authority score
6. **51** judged relevant outreach targets (LLM relevance gate + human-verified overrides)
7. **25** final recommendations below

**Score** = weighted blend of *competitor consensus* (how many of the four competitors the domain links to) and *authority* (Common Crawl harmonic-centrality rank). The LLM contributes only relevance/category labels — never the ranking.

## The 25 recommendations

| # | Domain | Why it matters | Suggested action | Consensus | Authority rank | Score |
|---|---|---|---|---|---|---|
| 1 | **hightouch.com** | Hightouch is a reverse-ETL partner platform with integration directories; strong opportunity for Omni listing on their destinations page. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 3,568 | 0.641 |
| 2 | **rudderstack.com** | RudderStack is a reverse-ETL/CDP partner platform with high authority; their integrations directory is a strong outreach target for Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 8,406 | 0.627 |
| 3 | **fivetran.com** | Fivetran is a complementary ELT partner, not a competitor; their integrations directory is a strong outreach target for BI platform listings. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 9,656 | 0.625 |
| 4 | **atlan.com** | Atlan is a data-catalog partner; their integrations directory lists BI tools and is an open outreach target. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 11,731 | 0.623 |
| 5 | **airbyte.com** | Airbyte is a complementary ELT partner, not a competitor; their integrations directory is a strong outreach target for BI platform listings. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 14,127 | 0.620 |
| 6 | **montecarlodata.com** | Monte Carlo Data is a data-observability platform (complementary partner, not competitor), but their vendor directory is curated and closed to non-portfolio companies. | Review manually. | 4/4 | 27,250 | 0.613 |
| 7 | **castordoc.com** | Castor is a data-catalog partner (not competitor); likely maintains integrations directory listing BI tools including Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 55,318 | 0.605 |
| 8 | **getcollate.io** | Collate is a data catalog/governance platform; likely maintains integrations directory listing BI tools including competitors—strong partnership opportunity. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 2,312,955 | 0.579 |
| 9 | **metaplane.dev** | Metaplane is a data-observability platform (not BI competitor); likely maintains integrations directory listing BI tools including Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 2,312,988 | 0.579 |
| 10 | **montecarlo.ai** | Monte Carlo is a data-observability partner (not competitor); their integrations directory is a strong outreach target for BI platform listings. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 10,217,235 | 0.571 |
| 11 | **entrepreneur.com** | Established business/tech publication linking to multiple BI platforms; strong authority (rank 648) and editorial credibility for guest content or product mention placement. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 648 | 0.552 |
| 12 | **welcometothejungle.com** | Welcome to the Jungle is a high-authority job/career platform; likely lists BI tools in tech stack or employer profiles—strong directory listing opportunity. | Submit a complete Omni listing to the directory. | 3/4 | 7,582 | 0.504 |
| 13 | **vendr.com** | Vendr is a software procurement directory; likely has open vendor submission or partnership opportunities for BI tools. | Submit a complete Omni listing to the directory. | 3/4 | 10,191 | 0.500 |
| 14 | **astronomer.io** | Astronomer (orchestration platform) lists BI tools in integrations directory; strong partner opportunity for Omni listing. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 23,530 | 0.489 |
| 15 | **rivery.io** | Rivery is an ELT/reverse-ETL partner platform with integrations directory; strong opportunity for Omni listing alongside competitors. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 28,394 | 0.487 |
| 16 | **dbta.com** | DBTA is established data-tech media covering BI platforms editorially; strong authority and relevant audience for guest content or product mentions. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 30,262 | 0.487 |
| 17 | **open-metadata.org** | Open Metadata is a data-governance community project; likely maintains curated integrations or tools directory where Omni can be listed. | Submit a complete Omni listing to the directory. | 3/4 | 76,032 | 0.477 |
| 18 | **risingwave.com** | RisingWave is a streaming data platform; links to BI tools suggest integrations/destinations directory—strong partnership opportunity. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 78,152 | 0.477 |
| 19 | **cube.dev** | Cube.dev is a data-orchestration/semantic-layer platform with integrations directory; strong partner fit for BI tool listings. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 93,783 | 0.476 |
| 20 | **datafold.com** | Datafold is a data observability platform (complementary partner, not competitor); likely maintains integrations or partner directory listing BI tools. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 109,569 | 0.474 |
| 21 | **getdot.ai** | Developer tool vendor linking to BI platforms; likely integrations or partner directory page—strong outreach target. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 140,539 | 0.472 |
| 22 | **siffletdata.com** | Sifflet is a data observability platform; likely maintains integrations or partner directory listing BI tools including competitors—strong partnership opportunity for Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 169,683 | 0.471 |
| 23 | **pocus.com** | Pocus is a data-driven sales platform; likely maintains integrations or partner directory listing BI tools including Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 212,960 | 0.469 |
| 24 | **i10x.ai** | Tech-focused domain linking to multiple BI platforms; likely editorial coverage of analytics tools with guest-content or mention opportunity. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 266,904 | 0.467 |
| 25 | **builtin.com** | Built In is a reputable tech careers and company news site; strong domain authority and editorial coverage of BI tools presents guest content or product mention opportunity. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 462,248 | 0.463 |

## Notable deliberate exclusions

High-authority domains in the gap that were **cut on actionability** — a reminder that this list optimizes for *outreach you can actually do*, not raw authority:

| Domain | Authority rank | Category | Reason |
|---|---|---|---|
| amazonaws.com | 32 | other | AWS is a cloud infrastructure vendor, not a BI platform or data-stack partner; links are likely product documentation or case studies, not editorial opportunities. |
| spotify.com | 36 | other | Spotify is a consumer music platform with no BI/analytics editorial presence; link to Hex is likely internal/technical, not editorial. |
| googleusercontent.com | 38 | other | googleusercontent.com is a Google infrastructure domain hosting user-generated content; not a valid outreach target. |
| t.me | 46 | other | t.me is Telegram's messaging platform; not a content/editorial site suitable for backlink outreach. |
| nih.gov | 49 | education_or_research | NIH.gov is a government research institution; links are editorial/contextual, not partnership-driven outreach targets. |
| stripe.com | 62 | other | Stripe is a payments platform, not a data/analytics ecosystem player; unlikely to feature BI tools prominently or accept outreach. |

## Insights beyond the list

- **Competitors earn links Omni cannot pitch for** — comparison/"vs" pages on other vendors' sites and organic community links (e.g. Hacker News at domain grain). The counter-move is content, not outreach: build Omni's own comparison pages targeting those keywords.
- **The integrations-directory motion dominates** the list: most recommendations are data-stack vendors whose directories already list BI tools. A single partner-page template + outreach sequence covers most of the 25.
- **Entity duplicates exist at domain grain** (e.g. montecarlo.ai vs montecarlodata.com) — treat them as one outreach target.

## Known limitations

- Classification is **name + link-signal based** (no page fetch at MVP); a future upgrade grounds the LLM with homepage titles/descriptions.
- The LLM competitor rule was violated in 2 of 150 classifications despite an explicit closed list (98.7% compliance) — documented in the Tech Spec; human review of 25 rows is the backstop.
- Link *presence* comes from the crawl window; a link dropped after June 2026 may persist until the next release refresh.

## Reproduce

`make setup && make run` — no API key required; see [README](../README.md). Data and classifications are pinned; re-runs are byte-identical.
