-- The deliverable mart (spec B13): up to top_n relevance-gated,
-- scored, enrichment-annotated referring domains. Contract-enforced
-- (spec B11). The inner join + is_relevant gate means rows appear
-- only for domains the enrich stage has classified as relevant —
-- before enrichment runs, this table is legitimately empty.

with opportunities as (

    select * from {{ ref('backlink_opportunities') }}

),

enrichment as (

    select
        domain,
        is_relevant,
        category,
        opportunity_type,
        rationale
    from {{ source('enrichment', 'domain_enrichment') }}

)

select
    opportunities.domain,
    opportunities.competitor_consensus,
    opportunities.links_to_sigma,
    opportunities.links_to_hex,
    opportunities.links_to_mode,
    opportunities.links_to_metabase,
    opportunities.harmonic_pos,
    opportunities.pagerank_pos,
    opportunities.opportunity_score,
    enrichment.category,
    enrichment.opportunity_type,
    enrichment.rationale
from opportunities
inner join enrichment
    on opportunities.domain = enrichment.domain
where enrichment.is_relevant
order by opportunities.opportunity_score desc
limit {{ var('top_n') }}
