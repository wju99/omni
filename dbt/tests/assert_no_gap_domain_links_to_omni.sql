-- The core invariant of the whole analysis: nothing in the gap set
-- links to Omni. Any returned row is a failure.

select opportunities.domain
from {{ ref('backlink_opportunities') }} as opportunities
inner join {{ ref('int_domain_signals') }} as signals
    on opportunities.domain = signals.domain
where signals.links_to_omni
