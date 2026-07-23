select
    domain_rev,
    harmonic_pos,
    harmonic_value,
    pagerank_pos,
    pagerank_value
from {{ source('webgraph', 'ranks') }}
