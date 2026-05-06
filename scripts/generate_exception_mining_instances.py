#!/usr/bin/env python3
"""Generate auditable exception-mining instance bundles."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from exception_mining.generation import generate_bundle


def _parse_params(value: str | None) -> dict[str, Any]:
    if value is None:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("--params-json must decode to a JSON object")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True, choices=[f"F0{i}" for i in range(1, 9)])
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--instance-id", default=None)
    parser.add_argument(
        "--params-json", default=None, help="JSON object overriding family defaults."
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run scripts/validate_exception_mining_bundle.py after writing the bundle.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the generator CLI."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    params = _parse_params(args.params_json)
    bundle_dir = generate_bundle(
        family=args.family,
        seed=args.seed,
        output_root=args.output_root,
        parameters=params,
        instance_id=args.instance_id,
    )

    if args.validate:
        subprocess.run(
            [
                sys.executable,
                "scripts/validate_exception_mining_bundle.py",
                str(bundle_dir),
                "--quiet",
            ],
            check=True,
        )

    print(json.dumps({"bundle_dir": str(bundle_dir)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
