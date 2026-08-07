# Estrategia de pruebas

## Objetivo aceptado

Probar reglas, aislamiento tenant, casos de uso, persistencia y límites arquitectónicos con la prueba más pequeña que dé confianza.

## Capas aceptadas

- Unitarias para Domain/Application puros.
- Integración para MongoDB y adaptadores.
- Arquitectura para dependencias y límites.
- API/contrato cuando exista Presentation definida.
- Un conjunto reducido end-to-end cuando los flujos se confirmen.

Fase 2 exige MongoDB real con replica set para índices, Decimal128,
transacciones, rollback y concurrencia; API/OpenAPI, arquitectura, Ruff, formato
y mypy forman el gate CI. No se fija cobertura numérica; cobertura alta no
reemplaza escenarios relevantes.
