"""Transform stage: run the dbt project (build = seed + run + test).

dbt SQL is deterministic and idempotent by construction (spec §6), so
this stage needs no manifest bookkeeping — a re-run rebuilds the same
tables from the same raw inputs. The caller must not hold an open
warehouse connection: DuckDB allows a single writing process, and dbt
opens its own.
"""

import subprocess
import sys

from pipeline import config


def run(select: str = None) -> None:
    """Invokes ``dbt build`` for the project.

    Args:
        select: Optional dbt node selection (e.g. one mart and its
            tests) for cheap partial rebuilds after enrichment.
    """
    command = [
        "dbt", "build",
        "--project-dir", "dbt",
        "--profiles-dir", "dbt",
    ]
    if select:
        command += ["--select", select]
    try:
        result = subprocess.run(command, cwd=config.ROOT_DIR)
    except FileNotFoundError:
        sys.exit("[transform] dbt executable not found — run via "
                 "`make run` / `uv run` so the project venv is "
                 "active")
    if result.returncode != 0:
        sys.exit(result.returncode)
