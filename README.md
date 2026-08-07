# Taller Back — fases 1 y 2

Backend local multi-tenant para identidad, Clientes y la operación completa de
un Taller: catálogos, Dispositivos, Órdenes, inventario mínimo, Pagos,
seguimiento público y comprobantes PDF. Expone una API FastAPI asíncrona,
valida identidades Auth0/OIDC y persiste en MongoDB con aislamiento por Taller.

## Requisitos

- Python 3.11
- Docker con Compose para MongoDB local
- Un API y aplicación configurados en Auth0 para emitir JWT RS256

## Inicio local

```bash
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
docker compose up -d
uvicorn app.main:app --reload
```

Configura en `.env` el issuer y audience reales de Auth0. No se almacenan
contraseñas ni secretos. OpenAPI queda en `http://localhost:8000/docs` y su
instantánea versionada en `openapi.json`.

## API

La base funcional es `/api/v1`. El contrato completo de Fase 2 está en
`docs/06-api/endpoints/phase-2.md`. Liveness está en `/health/live`; readiness
comprueba MongoDB, crea índices y sincroniza referencias ISO en `/health/ready`.

## Verificación

```bash
ruff check .
ruff format --check .
mypy app
python -m scripts.exportar_openapi --check
pytest -m "not integration"
pytest -m integration
```

Las pruebas de integración requieren el MongoDB local. El proyecto no declara
preparación para producción: TLS, backups, SLO, alertas y hosting están fuera de
alcance.
