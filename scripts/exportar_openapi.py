"""Exporta o verifica la instantánea OpenAPI canónica."""

import argparse
import json
from pathlib import Path

from app.main import app

DESTINO = Path(__file__).resolve().parents[1] / "openapi.json"


def contenido_actual() -> str:
    """Serializa de forma estable el contrato generado por FastAPI."""
    return (
        json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def main() -> int:
    """Escribe la instantánea o falla cuando existe deriva."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    argumentos = parser.parse_args()
    contenido = contenido_actual()
    if argumentos.check:
        if not DESTINO.exists() or DESTINO.read_text(encoding="utf-8") != contenido:
            print("openapi.json no coincide con el contrato generado")
            return 1
        return 0
    DESTINO.write_text(contenido, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
