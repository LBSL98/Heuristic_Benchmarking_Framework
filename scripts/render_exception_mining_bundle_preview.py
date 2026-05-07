#!/usr/bin/env python3
"""Render SVG graph previews from exception-mining generated-instance bundles."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from exception_mining.visualization import render_bundle_preview, result_to_dict


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Render an auditable SVG preview from stored exception-mining bundle artifacts."
        )
    )
    parser.add_argument(
        "--bundle", required=True, type=Path, help="Generated-instance bundle path."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output SVG path. Defaults to a graph_preview_<scope>_<encoding>.svg file in bundle.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help=(
            "Output JSON report path. Defaults to a visualization_report_<scope>_<encoding>.json "
            "file in bundle."
        ),
    )
    parser.add_argument(
        "--scope",
        choices=["auto", "full", "sample"],
        default="auto",
        help="Render full graph when feasible, sampled graph, or infer from stored artifacts.",
    )
    parser.add_argument(
        "--color-by",
        choices=["degree", "planted_block", "solver_partition", "none"],
        default="degree",
        help="Node color encoding.",
    )
    parser.add_argument(
        "--solver-partition",
        type=Path,
        default=None,
        help=(
            "Optional solver partition artifact. Required when --color-by solver_partition. "
            "Supports JSON object/list or text partition files."
        ),
    )
    parser.add_argument(
        "--validated-solver-artifact",
        action="store_true",
        help=(
            "Declare that --solver-partition points to a validated solver artifact. Without this "
            "flag, the rendered image is explicitly illustrative."
        ),
    )
    parser.add_argument("--title", default=None, help="Optional SVG title.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the visualization CLI."""

    args = build_parser().parse_args(argv)
    result = render_bundle_preview(
        bundle_path=args.bundle,
        output_path=args.output,
        report_path=args.report,
        scope=args.scope,
        color_by=args.color_by,
        solver_partition_path=args.solver_partition,
        validated_solver_artifact=args.validated_solver_artifact,
        title=args.title,
    )
    print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
