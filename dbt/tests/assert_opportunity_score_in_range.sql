-- Score components are designed to land in [0, 1]; a row outside
-- that range means a formula or weighting regression.

select
    domain,
    opportunity_score
from {{ ref('backlink_opportunities') }}
where opportunity_score < 0 or opportunity_score > 1
