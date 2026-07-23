"""Command-line entry point: ``python -m pipeline <command>``.

Commands are thin wrappers over pipeline modules so every stage stays
importable (and testable) on its own. ``run`` executes the stages in
order; stages not yet implemented are reported and skipped, so this
entrypoint is safe to wire into scheduling (Makefile / GitHub Actions
cron) from day one (spec B10).

Each stage opens and closes its own warehouse connection — DuckDB
allows a single writing process, and the transform stage hands the
file to dbt (a separate process).
"""

import argparse

from pipeline import config
from pipeline import db
from pipeline import extract
from pipeline import transform

_NOT_IMPLEMENTED = "not implemented yet (build plan: TECH_SPEC_DRAFT §8)"

# Ordered stages of one pipeline run. Entries become callables as
# each build step lands: enrich (step 4), report (step 5).
_STAGES = (
    ("extract", extract.run),
    ("transform", transform.run),
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


def cmd_extract(_args: argparse.Namespace) -> None:
    """Runs the extract stage (download + load) on its own."""
    extract.run()


def cmd_transform(args: argparse.Namespace) -> None:
    """Runs the dbt build on its own."""
    transform.run(select=args.select)


def cmd_reset(args: argparse.Namespace) -> None:
    """Clears manifest rows for a stage, forcing that work to redo."""
    con = db.connect()
    deleted = con.execute(
        "DELETE FROM pipeline_manifest "
        "WHERE release = ? AND stage = ? RETURNING 1",
        [config.RELEASE, args.stage],
    ).fetchall()
    print(f"reset {len(deleted)} manifest rows for stage "
          f"'{args.stage}'")
    con.close()


def cmd_run(_args: argparse.Namespace) -> None:
    """Runs all pipeline stages in order (idempotent, resumable)."""
    for name, stage_fn in _STAGES:
        if stage_fn is None:
            print(f"[run] {name}: {_NOT_IMPLEMENTED}")
            continue
        print(f"[run] {name}: start", flush=True)
        stage_fn()
        print(f"[run] {name}: done", flush=True)


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
        "extract", help="download webgraph + load raw tables"
    ).set_defaults(func=cmd_extract)
    transform_parser = sub.add_parser(
        "transform", help="run dbt build (seeds + models + tests)"
    )
    transform_parser.add_argument(
        "--select", default=None,
        help="dbt node selection for partial rebuilds")
    transform_parser.set_defaults(func=cmd_transform)
    reset = sub.add_parser(
        "reset", help="clear manifest rows for a stage (forces redo)"
    )
    reset.add_argument("stage", help="stage name, e.g. download/load")
    reset.set_defaults(func=cmd_reset)
    sub.add_parser(
        "run", help="run all stages"
    ).set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
