-- The brief caps the deliverable at top_n (25) referring domains.

select count(*) as row_count
from {{ ref('top_backlink_opportunities') }}
having count(*) > {{ var('top_n') }}
