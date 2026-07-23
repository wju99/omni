-- Deterministic pre-filter feeding the bounded LLM pass (spec B8):
-- the enrich stage classifies exactly these domains, cached by
-- domain so re-runs never re-call the API for a known domain.

select
    domain,
    competitor_consensus,
    harmonic_pos,
    opportunity_score
from {{ ref('backlink_opportunities') }}
order by opportunity_score desc
limit {{ var('shortlist_size') }}
