# Definition of Done

Una entrega está terminada solo cuando:

- Cumple todos los requisitos, reglas y criterios de aceptación en alcance.
- Respeta arquitectura hexagonal, límites de módulo y dirección de dependencias.
- Preserva aislamiento multi-tenant y valida contexto/Membresía sin confiar solo en entrada del cliente.
- Cumple reglas del proyecto, Google Python Style Guide, PEP 8, PEP 257 y type hints.
- Incluye pruebas unitarias, integración, repositorio, API y arquitectura que correspondan; todas las ejecutadas pasan.
- Cubre escenarios positivos, negativos y cross-tenant relevantes.
- Maneja errores explícitamente y no expone detalles sensibles.
- No contiene duplicación significativa ni abstracciones/dependencias innecesarias.
- Actualiza requisitos, decisiones y documentación afectada sin elevar pendientes silenciosamente.
- No contiene secretos, credenciales, datos sensibles innecesarios ni logs inseguros.
- No rompe contratos o módulos no relacionados; compatibilidad y migración están resueltas cuando aplican.
- El diff fue revisado, no contiene cambios fuera de alcance y la entrega informa verificaciones reales y pendientes.

Un porcentaje de cobertura o una revisión automática no sustituye estos puntos.
