-- The scored gap set (spec §5): domains that link to >=1 competitor
-- but NOT to Omni, after deterministic heuristic filters. Both the
-- enrichment shortlist and the final top list build on this mart.

with signals as (

    select * from {{ ref('int_domain_signals') }}

),

gap as (

    -- The hard gap filter — the thesis of the analysis.
    select *
    from signals
    where not links_to_omni
        and competitor_consensus >= 1

),

filtered as (

    select gap.*
    from gap
    -- Junk TLDs (seed); tld = first label of the reversed name.
    where string_split(gap.domain_rev, '.')[1] not in (
            select tld from {{ ref('excluded_tlds') }})
        -- Mega-platforms & utility domains (seed).
        and gap.domain not in (
            select domain from {{ ref('excluded_domains') }})
        -- Self/competitor properties are never outreach targets.
        and gap.domain not in (
            select domain from {{ ref('stg_webgraph__targets') }})
        -- Authority floor: unranked / ultra-deep domains are cut.
        and gap.harmonic_pos is not null
        and gap.harmonic_pos <= {{ var('rank_floor') }}

)

select
    domain,
    domain_rev,
    links_to_sigma,
    links_to_hex,
    links_to_mode,
    links_to_metabase,
    competitor_consensus,
    harmonic_pos,
    pagerank_pos,
    -- Authority: log-scaled inverse of harmonic rank -> (0, 1].
    1.0 / log10(harmonic_pos + 10) as authority_score,
    competitor_consensus / 4.0 as consensus_score,
    {{ var('authority_weight') }} * (1.0 / log10(harmonic_pos + 10))
        + {{ var('consensus_weight') }}
        * (competitor_consensus / 4.0)
        as opportunity_score
from filtered
