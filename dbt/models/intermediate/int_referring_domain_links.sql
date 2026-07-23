-- Grain: one row per (referring domain, competitor) pair.
-- Resolves the integer edge endpoints into named domains.

with target_vertices as (

    select
        targets.competitor,
        vertices.vertex_id
    from {{ ref('stg_webgraph__targets') }} as targets
    inner join {{ ref('stg_webgraph__vertices') }} as vertices
        on vertices.domain_rev = targets.domain_rev

),

links as (

    select
        edges.src_id,
        target_vertices.competitor
    from {{ ref('stg_webgraph__target_edges') }} as edges
    inner join target_vertices
        on edges.dst_id = target_vertices.vertex_id

)

-- distinct: a competitor with two domains (mode.com +
-- modeanalytics.com) must count once per referring domain.
select distinct
    referrers.domain_rev,
    referrers.domain,
    links.competitor
from links
inner join {{ ref('stg_webgraph__vertices') }} as referrers
    on links.src_id = referrers.vertex_id
