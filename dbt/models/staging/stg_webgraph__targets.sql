select
    competitor,
    domain,
    domain_rev
from {{ source('webgraph', 'targets') }}
