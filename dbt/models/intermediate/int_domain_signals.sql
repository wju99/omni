-- Grain: one row per referring domain, carrying every ranking
-- signal the marts need (spec §5): the gap flag, per-competitor
-- flags, consensus, and CC authority ranks (B7).

with links as (

    select * from {{ ref('int_referring_domain_links') }}

),

pivoted as (

    select
        domain_rev,
        domain,
        max(competitor = 'omni') as links_to_omni,
        max(competitor = 'sigma') as links_to_sigma,
        max(competitor = 'hex') as links_to_hex,
        max(competitor = 'mode') as links_to_mode,
        max(competitor = 'metabase') as links_to_metabase,
        count(distinct competitor)
            filter (where competitor != 'omni')
            as competitor_consensus
    from links
    group by domain_rev, domain

)

select
    pivoted.*,
    ranks.harmonic_pos,
    ranks.pagerank_pos
from pivoted
left join {{ ref('stg_webgraph__ranks') }} as ranks
    on pivoted.domain_rev = ranks.domain_rev
