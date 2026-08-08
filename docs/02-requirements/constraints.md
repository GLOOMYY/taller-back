# Restricciones

## Aceptadas

- Las fases 1 y 2 autorizan código, pruebas y CI; producción permanece fuera de alcance.
- MongoDB es la persistencia seleccionada.
- La arquitectura objetivo es un monolito modular hexagonal.
- El dominio usa nombres en español.
- Cada Taller es un tenant y el aislamiento es transversal.
- Los módulos y fases son los definidos en el roadmap; los candidatos no se promueven implícitamente.
- No se fijan esquemas concretos de base de datos antes de conocer agregados y patrones de consulta.
- FastAPI es el adaptador HTTP; la API emite y verifica JWT locales con PyJWT y PyMongo Async es el driver MongoDB.
- ReportLab es el adaptador PDF de fase 2 y debe ejecutarse mediante
  `asyncio.to_thread`.
- La base existente no contiene datos que migrar: los campos nuevos obligatorios
  de Taller se aplican desde creación sin migración retrospectiva.

## Precedencia de decisiones

1. Requisitos y reglas aceptados del proyecto.
2. ADR aceptados.
3. Documentos especializados del área.
4. Convenciones propuestas.

Si dos fuentes aceptadas se contradicen, se detiene la implementación afectada y se registra una decisión pendiente; no se elige silenciosamente.
