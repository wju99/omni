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
6. **63** judged relevant outreach targets by the LLM relevance gate
7. **25** final recommendations below

**Score** = weighted blend of *competitor consensus* (how many of the four competitors the domain links to) and *authority* (Common Crawl harmonic-centrality rank). The LLM contributes only relevance/category labels — never the ranking.

## The 25 recommendations

| # | Domain | Why it matters | Suggested action | Consensus | Authority rank | Score |
|---|---|---|---|---|---|---|
| 1 | **hightouch.com** | Hightouch is a reverse-ETL partner platform with integration directories; strong opportunity for Omni listing on their destinations page. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 3,568 | 0.641 |
| 2 | **rudderstack.com** | RudderStack is a reverse-ETL/CDP partner platform with high authority; their integrations directory is a strong backlink opportunity. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 8,406 | 0.627 |
| 3 | **fivetran.com** | Fivetran is a key ELT partner with integration directories; strong opportunity for Omni destination listing. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 9,656 | 0.625 |
| 4 | **atlan.com** | Atlan is a data catalog/governance platform (partner, not competitor); their integrations directory is a high-authority outreach target for BI tools. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 11,731 | 0.623 |
| 5 | **airbyte.com** | Airbyte is a complementary ELT platform with integration directories; strong partnership opportunity for Omni listing. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 14,127 | 0.620 |
| 6 | **montecarlodata.com** | Monte Carlo is a data observability partner with integration directory; strong authority and relevant audience for Omni placement. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 27,250 | 0.613 |
| 7 | **castordoc.com** | Castor is a data catalog (complementary partner, not competitor); likely maintains integrations directory listing BI tools including Omni. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 55,318 | 0.605 |
| 8 | **getcollate.io** | Collate is a data catalog/governance platform; likely maintains integrations directory listing BI tools including competitors. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 2,312,955 | 0.579 |
| 9 | **metaplane.dev** | Metaplane is a data observability platform with integration/destination directory; strong partner opportunity for Omni listing. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 2,312,988 | 0.579 |
| 10 | **blazesql.com** | BlazeSql is a SQL IDE/query tool that integrates BI platforms; likely maintains integrations directory listing Omni as alternative. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 7,729,119 | 0.573 |
| 11 | **montecarlo.ai** | Monte Carlo is a data observability partner (not competitor); their integrations directory is a strong backlink opportunity. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 4/4 | 10,217,235 | 0.571 |
| 12 | **entrepreneur.com** | High-authority business/tech publication linking to multiple BI platforms; strong guest content or feature opportunity. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 648 | 0.552 |
| 13 | **bvp.com** | BVP is a respected venture-capital firm with high authority; likely maintains curated BI-tool directory or comparison content suitable for partnership outreach. | Submit a complete Omni listing to the directory. | 3/4 | 6,263 | 0.507 |
| 14 | **vendr.com** | Vendr is a SaaS procurement directory; listing Omni alongside competitors suggests strong directory inclusion opportunity. | Submit a complete Omni listing to the directory. | 3/4 | 10,191 | 0.500 |
| 15 | **astronomer.io** | Astronomer (orchestration platform) lists BI tools in integrations directory; strong partner opportunity for Omni inclusion. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 23,530 | 0.489 |
| 16 | **rivery.io** | Rivery is an ELT/ETL partner platform with integration directory; strong candidate for Omni integration listing. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 28,394 | 0.487 |
| 17 | **infotech.com** | Established tech publication covering BI platforms; strong authority and editorial credibility make it a viable outreach target for Omni coverage. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 29,904 | 0.487 |
| 18 | **dbta.com** | DBTA is established tech media covering data platforms; strong authority and editorial credibility make it viable for feature coverage or analyst mention. | Pitch a briefing or story angle; aim for a linked product mention. | 3/4 | 30,262 | 0.487 |
| 19 | **berkeley.edu** | UC Berkeley's domain has high authority and mentions analytics tools in educational context; strong opportunity for guest content or curriculum integration. | Pitch a briefing or story angle; aim for a linked product mention. | 2/4 | 123 | 0.485 |
| 20 | **open-metadata.org** | Open Metadata is a data governance community project; listing Omni alongside competitors suggests directory inclusion opportunity. | Submit a complete Omni listing to the directory. | 3/4 | 76,032 | 0.477 |
| 21 | **cube.dev** | Cube.dev is a data-modeling/semantic-layer platform (partner, not competitor); likely maintains integrations directory listing BI tools including Omni's competitors. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 93,783 | 0.476 |
| 22 | **datafold.com** | Datafold is a data observability platform; integrations pages for complementary data-stack tools are strong partnership/backlink opportunities. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 109,569 | 0.474 |
| 23 | **getdot.ai** | Developer tool vendor linking to multiple BI platforms; likely integrations or partner directory page suitable for Omni inclusion. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 140,539 | 0.472 |
| 24 | **siffletdata.com** | Sifflet is a data observability platform; their integrations directory likely lists BI tools as destinations for data quality insights. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 169,683 | 0.471 |
| 25 | **pocus.com** | Pocus is a data-driven sales platform that likely maintains integrations or partnerships directory; strong authority and multi-competitor links suggest BI tool coverage. | Pitch Omni for their integrations/destinations directory; offer a co-marketing blurb or joint documentation. | 3/4 | 212,960 | 0.469 |

## Notable deliberate exclusions

High-authority domains in the gap that were **cut on actionability** — a reminder that this list optimizes for *outreach you can actually do*, not raw authority:

| Domain | Authority rank | Category | Reason |
|---|---|---|---|
| amazonaws.com | 32 | data_platform_vendor | AWS is a cloud infrastructure vendor, not a BI platform, but owned by Amazon (which owns QuickSight). Not an outreach target. |
| spotify.com | 36 | other | Spotify is a music streaming platform with no BI/analytics focus; link to Hex is likely incidental or unrelated to data analytics. |
| googleusercontent.com | 38 | junk_or_spam | googleusercontent.com is a Google infrastructure domain hosting user-generated content; not a viable outreach target. |
| t.me | 46 | junk_or_spam | t.me is Telegram's messaging platform; not a content/editorial domain suitable for BI platform backlinks. |
| nih.gov | 49 | education_or_research | NIH.gov is a government research institution; Metabase mention likely incidental to research infrastructure, not editorial opportunity. |
| stripe.com | 62 | other | Stripe is a payments platform, not a data/analytics ecosystem player; unlikely to feature BI tools prominently or accept guest content on analytics topics. |

## Insights beyond the list

- **Competitors earn links Omni cannot pitch for** — comparison/"vs" pages on other vendors' sites and organic community links (e.g. Hacker News at domain grain). The counter-move is content, not outreach: build Omni's own comparison pages targeting those keywords.
- **The integrations-directory motion dominates** the list: most recommendations are data-stack vendors whose directories already list BI tools. A single partner-page template + outreach sequence covers most of the 25.
- **Entity duplicates exist at domain grain** (e.g. montecarlo.ai vs montecarlodata.com) — treat them as one outreach target.

## Known limitations

- Classification is **name + link-signal based** (no page fetch at MVP); a week-1 upgrade grounds the LLM with homepage titles/descriptions.
- The LLM competitor rule was violated in 2 of 150 classifications despite an explicit closed list (98.7% compliance) — documented in the Tech Spec; human review of 25 rows is the backstop.
- Link *presence* comes from the crawl window; a link dropped after June 2026 may persist until the next release refresh.

## Reproduce

`make setup && make run` — no API key required; see [README](../README.md). Data and classifications are pinned; re-runs are byte-identical.
