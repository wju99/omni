select
    id as vertex_id,
    domain_rev,
    -- CC stores reversed names (co.omni); un-reverse for humans.
    array_to_string(list_reverse(string_split(domain_rev, '.')), '.')
        as domain,
    n_hosts
from {{ source('webgraph', 'vertices') }}
