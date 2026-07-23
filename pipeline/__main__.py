"""Command-line entry point: ``python -m pipeline <command>``.

Commands are thin wrappers over pipeline modules so every stage stays
importable (and testable) on its own. ``run`` executes the stages in
order; stages not yet implemented are reported and skipped, so this
entrypoint is safe to wire into scheduling (Makefile / GitHub Actions
cron) from day one (spec B10).
"""

import argparse

from pipeline import config
from pipeline import db

_NOT_IMPLEMENTED = "not implemented yet (build plan: TECH_SPEC_DRAFT §8)"

# Ordered stages of one pipeline run. Values become callables as each
# build step lands: extract (step 2), transform (step 3), enrich
# (step 4), report (step 5).
_STAGES = (
    ("extract", None),
    ("transform", None),
    ("enrich", None),
    ("report", None),
)


def cmd_init(_args: argparse.Namespace) -> None:
    """Creates the DuckDB warehouse, schemas, and manifest."""
    con = db.connect()
    con.close()
    print(f"warehouse ready: {config.DB_PATH}")


def cmd_status(_args: argparse.Namespace) -> None:
    """Prints manifest progress and table row counts."""
    con = db.connect()
    print(f"release: {config.RELEASE}")
    rows = db.status_summary(con)
    if not rows:
        print("manifest: empty (nothing has run yet)")
    else:
        print(f"{'stage':<12} {'status':<12} {'units':>6} "
              f"{'attempts':>9}")
        for stage, status, units, attempts, _updated in rows:
            print(f"{stage:<12} {status:<12} {units:>6} "
                  f"{attempts:>9}")
    print("\ntables:")
    for schema, table, count in db.table_summary(con):
        print(f"  {schema}.{table}: {count:,} rows")
    con.close()


def cmd_run(_args: argparse.Namespace) -> None:
    """Runs all pipeline stages in order (idempotent, resumable)."""
    con = db.connect()
    for name, stage_fn in _STAGES:
        if stage_fn is None:
            print(f"[run] {name}: {_NOT_IMPLEMENTED}")
            continue
        print(f"[run] {name}: start")
        stage_fn(con)
        print(f"[run] {name}: done")
    con.close()


def main(argv=None) -> None:
    """Parses arguments and dispatches to a command."""
    parser = argparse.ArgumentParser(
        prog="python -m pipeline",
        description=(
            "Backlink gap-analysis pipeline over the Common Crawl "
            "domain webgraph."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "init", help="create warehouse + manifest"
    ).set_defaults(func=cmd_init)
    sub.add_parser(
        "status", help="show manifest + tables"
    ).set_defaults(func=cmd_status)
    sub.add_parser(
        "run", help="run all stages"
    ).set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
