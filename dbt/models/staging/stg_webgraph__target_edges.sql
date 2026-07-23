select
    src_id,
    dst_id
from {{ source('webgraph', 'target_edges') }}
