"""Controles ejecutables de las reglas de dependencia hexagonal."""

import ast
from pathlib import Path

APP = Path(__file__).parents[2] / "app"


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_domain_no_importa_frameworks_ni_adaptadores() -> None:
    prohibidos = ("fastapi", "pymongo", "app.core")
    for path in APP.glob("modules/*/domain/**/*.py"):
        for imported in imports(path):
            assert not imported.startswith(prohibidos), f"{path} importa {imported}"
            assert ".infrastructure" not in imported
            assert ".presentation" not in imported


def test_presentation_no_importa_mongodb_ni_infrastructure() -> None:
    for path in APP.glob("modules/*/presentation/**/*.py"):
        for imported in imports(path):
            assert not imported.startswith("pymongo"), f"{path} importa MongoDB"
            assert ".infrastructure" not in imported, f"{path} accede a Infrastructure"
