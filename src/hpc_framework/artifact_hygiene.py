"""Utilitários de higiene para distinguir artefatos legados de artefatos canônicos."""

from __future__ import annotations

import shutil
from pathlib import Path


def is_legacy_result_name(name: str) -> bool:
    """Detecta nomes antigos de resultados que não codificam a configuração experimental."""
    if "__metis__seed" in name:
        return True
    if "__kahip__seed" in name:
        return True
    return "__greedy__seed" in name


def is_legacy_workdir_name(name: str) -> bool:
    """Detecta diretórios de trabalho antigos sem parâmetros experimentais no namespace."""
    if "run_metis__" in name and "__seed" in name and "__k" not in name and "__b" not in name:
        return True
    return bool(
        "run_kahip__" in name and "__seed" in name and "__k" not in name and "__b" not in name
    )


def quarantine_legacy_artifacts(raw_dir: Path) -> list[str]:
    """Move artefatos legados de `raw_dir` para `_legacy_quarantine`.

    Retorna a lista de nomes movidos.
    """
    raw_dir = Path(raw_dir)
    archive_dir = raw_dir / "_legacy_quarantine"
    moved: list[str] = []

    for entry in raw_dir.iterdir():
        if entry.name == "_legacy_quarantine":
            continue

        should_move = False
        if (
            entry.is_file()
            and is_legacy_result_name(entry.name)
            or entry.is_dir()
            and is_legacy_workdir_name(entry.name)
        ):
            should_move = True

        if should_move:
            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(entry), str(archive_dir / entry.name))
            moved.append(entry.name)

    return moved
