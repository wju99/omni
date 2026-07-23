"""Central configuration: release, targets, URLs, paths, models.

All pipeline stages read from this module so a future release bump
(or target-set change) is a one-line edit. Secrets come from the
environment; a local ``.env`` file is loaded as a convenience if
present.
"""

import os
import pathlib

# --- Repo paths --------------------------------------------------------

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"          # gitignored inputs/warehouse
ARTIFACTS_DIR = ROOT_DIR / "artifacts"  # committed pipeline outputs
DB_PATH = DATA_DIR / "omni.duckdb"


def _load_dotenv(path: pathlib.Path = ROOT_DIR / ".env") -> None:
    """Loads KEY=VALUE lines from .env into os.environ (no overrides).

    Args:
        path: Location of the .env file; a missing file is a no-op.
    """
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

# --- Common Crawl release (spec B2/B5) ---------------------------------

# Single domain-webgraph release aggregating the two collections named
# by the brief: May 2026 (CC-MAIN-2026-21) + June 2026
# (CC-MAIN-2026-25).
RELEASE = "cc-main-2026-apr-may-jun"
CRAWL_INPUTS = ("CC-MAIN-2026-21", "CC-MAIN-2026-25")

_BASE_URL = (
    "https://data.commoncrawl.org/projects/hyperlinkgraph/"
    f"{RELEASE}/domain"
)

# Webgraph artifacts. Verified live 2026-07-22 via HTTP HEAD
# (Accept-Ranges: bytes -> chunked, resumable downloads):
#   vertices 0.9 GB gz | edges 14.6 GB gz | ranks 2.4 GB gz
WEBGRAPH_FILES = {
    "vertices": f"{_BASE_URL}/{RELEASE}-domain-vertices.txt.gz",
    "edges": f"{_BASE_URL}/{RELEASE}-domain-edges.txt.gz",
    "ranks": f"{_BASE_URL}/{RELEASE}-domain-ranks.txt.gz",
}

DOWNLOAD_DIR = DATA_DIR / "cc" / RELEASE

# --- Targets (spec B3) --------------------------------------------------

# Competitor key -> registered domains counted as that competitor.
# modeanalytics.com is kept as a legacy alias for mode.com
# (pre-rebrand backlinks still point at it).
TARGETS = {
    "omni": ("omni.co",),
    "sigma": ("sigmacomputing.com",),
    "hex": ("hex.tech",),
    "mode": ("mode.com", "modeanalytics.com"),
    "metabase": ("metabase.com",),
}
OMNI_KEY = "omni"


def reverse_domain(domain: str) -> str:
    """Returns the reversed-host notation used by CC webgraph files.

    Example: ``omni.co`` -> ``co.omni``.

    Args:
        domain: Registered domain in normal notation.

    Returns:
        The domain with labels reversed, as found in webgraph
        vertices.
    """
    return ".".join(reversed(domain.split(".")))


# --- Output & enrichment (spec B4/B8) -----------------------------------

# The brief caps the deliverable at 25 referring domains.
TOP_N = 25

ANTHROPIC_MODEL = "claude-haiku-4-5"
