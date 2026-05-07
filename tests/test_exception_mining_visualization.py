"""Tests for exception-mining visualization preview rendering."""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path

from exception_mining.visualization import render_bundle_preview


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_minimal_bundle(bundle: Path) -> None:
    bundle.mkdir(parents=True)

    instance = {
        "schema_version": "exception-mining-1.0",
        "epsilon": 0.03,
        "instance_id": "toy_visual",
        "generator": "unit_test",
        "seed": 123,
        "created_at": "2026-05-07T00:00:00+00:00",
        "nodes": [
            {"id": 0, "planted_block": 0},
            {"id": 1, "planted_block": 0},
            {"id": 2, "planted_block": 1},
            {"id": 3, "planted_block": 1},
        ],
        "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
        "instance_metrics": {"num_vertices": 4, "num_edges": 4},
    }
    with gzip.open(bundle / "instance.json.gz", "wt", encoding="utf-8") as handle:
        json.dump(instance, handle)

    (bundle / "graph_edges.edgelist").write_text("0 1\n1 2\n2 3\n3 0\n", encoding="utf-8")

    _write_json(
        bundle / "graph_preview_layout.json",
        {
            "layout_algorithm": "fixed_unit_square",
            "layout_seed": 123,
            "layout_parameters": {"source": "unit_test"},
            "layout_scope": "full",
            "node_positions": {
                "0": [0.0, 0.0],
                "1": [1.0, 0.0],
                "2": [1.0, 1.0],
                "3": [0.0, 1.0],
            },
        },
    )
    _write_json(
        bundle / "graph_preview_sample.json",
        {
            "sampling_policy": "full_graph",
            "sample_seed": 123,
            "sampled_nodes": [0, 1, 2, 3],
            "sampled_edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
        },
    )
    _write_json(
        bundle / "visualization_metadata.json",
        {
            "available_encodings": [
                "degree",
                "connected_component_id",
                "planted_block",
                "solver_partition",
            ],
            "layout_file": "graph_preview_layout.json",
            "sample_file": "graph_preview_sample.json",
            "notes": "unit test visualization metadata",
        },
    )


def test_render_bundle_preview_degree_svg_and_report(tmp_path: Path) -> None:
    """Render a degree-colored SVG and audit report from stored bundle artifacts."""

    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)

    result = render_bundle_preview(bundle, scope="auto", color_by="degree")

    svg_path = Path(result.output_path)
    report_path = Path(result.report_path)

    assert svg_path.exists()
    assert report_path.exists()
    assert result.image_scope == "full"
    assert result.color_by == "degree"
    assert result.rendered_nodes == 4
    assert result.rendered_edges == 4
    assert result.illustrative is True

    svg = svg_path.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "scope=full" in svg
    assert "layout=fixed_unit_square" in svg
    assert "illustrative preview only" in svg

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["image_scope"] == "full"
    assert report["layout_algorithm"] == "fixed_unit_square"
    assert report["layout_seed"] == 123
    assert report["color_by"] == "degree"
    assert report["illustrative"] is True


def test_render_bundle_preview_planted_block_coloring(tmp_path: Path) -> None:
    """Render a planted-block-colored SVG when generated labels are available."""

    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)

    result = render_bundle_preview(bundle, scope="sample", color_by="planted_block")
    report = json.loads(Path(result.report_path).read_text(encoding="utf-8"))
    svg = Path(result.output_path).read_text(encoding="utf-8")

    assert result.image_scope == "sample"
    assert report["color_by"] == "planted_block"
    assert report["warnings"] == []
    assert "label=0" in svg
    assert "label=1" in svg


def test_visualization_cli_renders_svg(tmp_path: Path) -> None:
    """Render an SVG through the command-line script."""

    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)
    output = tmp_path / "preview.svg"
    report = tmp_path / "report.json"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/render_exception_mining_bundle_preview.py",
            "--bundle",
            str(bundle),
            "--output",
            str(output),
            "--report",
            str(report),
            "--color-by",
            "planted_block",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    cli_payload = json.loads(completed.stdout)
    assert cli_payload["output_path"] == str(output.resolve())
    assert output.exists()
    assert report.exists()

    report_payload = json.loads(report.read_text(encoding="utf-8"))
    assert report_payload["image_type"] == "svg"
    assert report_payload["color_by"] == "planted_block"
