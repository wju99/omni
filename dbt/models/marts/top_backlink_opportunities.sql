-- The deliverable mart (spec B13): up to top_n relevance-gated,
-- scored, enrichment-annotated referring domains. Contract-enforced
-- (spec B11). The inner join + relevance gate means rows appear
-- only for domains the enrich stage has classified — before
-- enrichment runs, this table is legitimately empty.
--
-- Relevance = coalesce(human override, LLM verdict): the LLM
-- proposes, human-verified rows in the enrichment_overrides seed
-- always win (versioned human-in-the-loop, immune to prompt churn).

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

),

overrides as (

    select
        domain,
        is_relevant
    from {{ ref('enrichment_overrides') }}

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
left join overrides
    on opportunities.domain = overrides.domain
where coalesce(overrides.is_relevant, enrichment.is_relevant)
order by opportunities.opportunity_score desc
limit {{ var('top_n') }}
