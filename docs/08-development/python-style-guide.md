# Guía de estilo Python

## Reglas aceptadas

- Type hints en interfaces, funciones y métodos; excepciones solo si se documentan.
- Docstrings conforme a PEP 257 y estilo Google cuando aporten contrato, intención o contexto; no repetir literalmente una firma obvia.
- Nombres claros, imports explícitos y constantes con significado.
- Evitar estado global mutable, efectos laterales ocultos y argumentos mutables por defecto.
- Capturar excepciones específicas; no usar `except` amplio sin causa justificada y manejo explícito.
- Mantener funciones enfocadas y flujo legible.

## Pendiente

Versión de Python, formatter, linter, type checker, longitud de línea y política exacta de cobertura de tipos.
