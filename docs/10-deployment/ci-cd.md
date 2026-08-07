# CI/CD

## Aceptado para fases 1 y 2

GitHub Actions instala dependencias fijadas y ejecuta Ruff, formato, mypy,
pruebas unitarias/API/arquitectura y pruebas de integración sobre el replica set
de Docker Compose. No se configura CD en fase 1.

No desplegar si fallan controles obligatorios ni incluir secretos en salida. Separar construcción y promoción reduce divergencia.

Firma de artefactos y despliegue permanecen fuera de alcance.
