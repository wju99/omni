"""Extract stage: resumable webgraph download + filtered raw load.

Download: each file is fetched in fixed-size byte-range chunks
written at their offsets into a preallocated sparse file; every chunk
is a manifest unit (spec B9), so an interrupted download resumes at
the first incomplete chunk on the next run (the CC origin supports
byte ranges — verified in spec §3).

Load: raw tables land in the ``raw`` schema (spec B16); edges are
filtered to in-edges of the target domains while streaming (spec B6),
so the graph's billions of edges never materialize locally.

File formats (verified live 2026-07-22, spec §3):
    vertices  id \\t domain_rev \\t n_hosts          (no header)
    edges     src_id \\t dst_id                      (no header)
    ranks     harmonic pos/val, pagerank pos/val,
              domain_rev, n_hosts                    ('#' header row)
"""

import shutil
import sys
import time

import requests
import tqdm

from pipeline import config
from pipeline import db

CHUNK_BYTES = 64 * 1024 * 1024   # Ranged-download unit (64 MiB).
_IO_BYTES = 4 * 1024 * 1024      # Streaming copy buffer.
_MIN_FREE_BYTES = 2 * 1024**3    # Bare workspace floor (resume path).
_DISK_BUFFER_BYTES = 7 * 1024**3  # DuckDB tables + working headroom.
_TIMEOUT = (10, 120)             # (connect, read) seconds.


def chunk_plan(total_bytes: int, chunk_bytes: int = CHUNK_BYTES):
    """Returns the ranged-download chunks for a file.

    Args:
        total_bytes: Size of the remote file.
        chunk_bytes: Bytes per chunk.

    Returns:
        List of (index, first_byte, last_byte_inclusive) tuples
        covering the file exactly; the final chunk may be short.
    """
    chunks = []
    for index, start in enumerate(range(0, total_bytes, chunk_bytes)):
        end = min(start + chunk_bytes, total_bytes) - 1
        chunks.append((index, start, end))
    return chunks


def _remote_size(url: str) -> int:
    response = requests.head(url, timeout=_TIMEOUT,
                             allow_redirects=True)
    response.raise_for_status()
    return int(response.headers["Content-Length"])


def _local_path(name: str):
    url = config.WEBGRAPH_FILES[name]
    return config.DOWNLOAD_DIR / url.rsplit("/", 1)[-1]


def _preallocate(path, size: int) -> None:
    """Creates a sparse file of the expected size if not present."""
    if path.exists() and path.stat().st_size == size:
        return
    with open(path, "wb") as handle:
        if size:
            handle.seek(size - 1)
            handle.write(b"\0")


def _fetch_chunk(url: str, start: int, end: int, path) -> None:
    headers = {"Range": f"bytes={start}-{end}"}
    with requests.get(url, headers=headers, stream=True,
                      timeout=_TIMEOUT) as response:
        response.raise_for_status()
        with open(path, "r+b") as handle:
            handle.seek(start)
            for piece in response.iter_content(_IO_BYTES):
                handle.write(piece)


def download_file(con, name: str) -> bool:
    """Downloads one webgraph file resumably.

    Args:
        con: Warehouse connection (manifest bookkeeping).
        name: Key into config.WEBGRAPH_FILES.

    Returns:
        True when every chunk of the file is complete.
    """
    url = config.WEBGRAPH_FILES[name]
    size = _remote_size(url)
    path = _local_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    _preallocate(path, size)
    # Disk guard on what is actually LEFT to fetch (a resumed or
    # re-run download with all chunks done needs no headroom —
    # found via reviewer-workflow replication).
    remaining = size - _downloaded_bytes(con, name)
    if remaining > 0:
        _require_free(
            remaining + _DISK_BUFFER_BYTES,
            f"downloading {name} "
            f"({remaining / 1024**3:.1f} GiB remaining)")
    failed = 0
    # disable=None auto-hides the bar when not attached to a TTY
    # (e.g. background runs); the periodic prints below cover logs.
    progress = tqdm.tqdm(total=size, unit="B", unit_scale=True,
                         desc=f"download {name}", mininterval=5,
                         disable=None)
    for index, start, end in chunk_plan(size):
        unit = f"{name}:{index:05d}"
        length = end - start + 1
        if not db.claim(con, "download", unit):
            progress.update(length)
            continue
        if index % 32 == 0:
            print(f"[download {name}] chunk {index} "
                  f"({start / size:.0%})", flush=True)
        try:
            _fetch_chunk(url, start, end, path)
        except Exception as error:  # Flaky seam: record, keep going.
            db.mark_failed(con, "download", unit, error)
            failed += 1
        else:
            db.mark_done(con, "download", unit, detail=str(length))
            progress.update(length)
    progress.close()
    return failed == 0


def download_all(con) -> bool:
    """Downloads every webgraph file; True if all are complete."""
    complete = True
    for name in config.WEBGRAPH_FILES:
        if not download_file(con, name):
            complete = False
    return complete


# --- Load into DuckDB raw schema ----------------------------------------


def _count(con, table: str) -> int:
    return con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def _load_targets(con) -> int:
    """Materializes the config target set as a raw dimension table."""
    con.execute(
        "CREATE OR REPLACE TABLE raw.targets ("
        "competitor VARCHAR, domain VARCHAR, domain_rev VARCHAR)")
    rows = []
    for key, domains in config.TARGETS.items():
        for domain in domains:
            rows.append((key, domain, config.reverse_domain(domain)))
    con.executemany("INSERT INTO raw.targets VALUES (?, ?, ?)", rows)
    return len(rows)


def _load_vertices(con) -> int:
    path = _local_path("vertices")
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.vertices AS
        SELECT * FROM read_csv('{path}', delim='\t', header=false,
            columns={{'id': 'BIGINT', 'domain_rev': 'VARCHAR',
                      'n_hosts': 'BIGINT'}})
    """)
    return _count(con, "raw.vertices")


def _load_ranks(con) -> int:
    path = _local_path("ranks")
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.ranks AS
        SELECT * FROM read_csv('{path}', delim='\t', header=false,
            skip=1,
            columns={{'harmonic_pos': 'BIGINT',
                      'harmonic_value': 'DOUBLE',
                      'pagerank_pos': 'BIGINT',
                      'pagerank_value': 'DOUBLE',
                      'domain_rev': 'VARCHAR',
                      'n_hosts': 'BIGINT'}})
    """)
    return _count(con, "raw.ranks")


def _load_edges(con) -> int:
    """Streams the edges file, keeping only target in-edges (B6)."""
    path = _local_path("edges")
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.target_edges AS
        SELECT src_id, dst_id
        FROM read_csv('{path}', delim='\t', header=false,
            columns={{'src_id': 'BIGINT', 'dst_id': 'BIGINT'}})
        WHERE dst_id IN (
            SELECT vertices.id
            FROM raw.vertices AS vertices
            JOIN raw.targets AS targets
                ON vertices.domain_rev = targets.domain_rev)
    """)
    return _count(con, "raw.target_edges")


_LOAD_STEPS = (
    ("targets", _load_targets),
    ("vertices", _load_vertices),
    ("ranks", _load_ranks),
    ("target_edges", _load_edges),
)


def load_all(con) -> None:
    """Loads raw tables into DuckDB; completed units are skipped."""
    for unit, load_fn in _LOAD_STEPS:
        if not db.claim(con, "load", unit):
            print(f"[load] {unit}: already loaded, skipping")
            continue
        started = time.time()
        try:
            rows = load_fn(con)
        except Exception as error:
            db.mark_failed(con, "load", unit, error)
            raise
        db.mark_done(con, "load", unit, detail=f"{rows} rows")
        elapsed = time.time() - started
        print(f"[load] {unit}: {rows:,} rows in {elapsed:.0f}s",
              flush=True)


def _report_target_coverage(con) -> None:
    """Prints per-target vertex presence; aborts if omni is absent."""
    rows = con.execute("""
        SELECT targets.competitor, targets.domain, vertices.id
        FROM raw.targets AS targets
        LEFT JOIN raw.vertices AS vertices
            ON vertices.domain_rev = targets.domain_rev
        ORDER BY targets.competitor, targets.domain
    """).fetchall()
    missing_omni = False
    print("[extract] target vertex coverage:")
    for competitor, domain, vertex_id in rows:
        marker = "OK" if vertex_id is not None else "MISSING"
        print(f"  {competitor:<10} {domain:<22} {marker}")
        if competitor == config.OMNI_KEY and vertex_id is None:
            missing_omni = True
    if missing_omni:
        sys.exit("[extract] omni.co not found in vertices — gap "
                 "analysis impossible; investigate before continuing")


def _downloaded_bytes(con, name: str) -> int:
    """Returns bytes already fetched for a file, per the manifest."""
    row = con.execute(
        "SELECT coalesce(sum(cast(detail AS BIGINT)), 0) "
        "FROM pipeline_manifest "
        "WHERE release = ? AND stage = 'download' "
        "AND unit LIKE ? AND status = 'done'",
        [config.RELEASE, f"{name}:%"],
    ).fetchone()
    return int(row[0])


def _require_free(needed: int, context: str) -> None:
    """Aborts unless the data volume has `needed` bytes free."""
    free = shutil.disk_usage(config.DATA_DIR).free
    if free < needed:
        sys.exit(
            f"[extract] only {free / 1024**3:.1f} GiB free; need "
            f"~{needed / 1024**3:.1f} GiB for {context}. "
            "Free space and re-run.")


def _check_disk() -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _require_free(_MIN_FREE_BYTES, "pipeline workspace")


def run() -> None:
    """Runs the extract stage end to end (download + load).

    Opens and closes its own warehouse connection so no lock is held
    once the stage returns (DuckDB allows a single writing process —
    the next stage, dbt, opens its own).
    """
    _check_disk()
    con = db.connect()
    try:
        if not download_all(con):
            print("[extract] retrying failed chunks...")
            if not download_all(con):
                sys.exit("[extract] download chunks still failing "
                         "after retry; re-run to resume from the "
                         "manifest")
        load_all(con)
        _report_target_coverage(con)
    finally:
        con.close()
