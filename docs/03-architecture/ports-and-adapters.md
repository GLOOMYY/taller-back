# Puertos y adaptadores

## Puertos de entrada

**Aceptado para fase 1:** casos de uso públicos recibidos por Presentation que
expresan identidad/contexto tenant y no detalles HTTP.

## Puertos de salida

**Aceptado para fase 1:** contratos `Protocol` enfocados para persistencia,
identidad y generación de identificadores.

## Adaptadores de entrada

FastAPI es el adaptador de entrada **Aceptado** para fase 1. Otros canales no
están confirmados.

## Adaptadores de salida

PyMongo Async es el adaptador de persistencia y Auth0/PyJWT el adaptador de
identidad de fase 1. Mensajería, archivos y otros terceros no están confirmados.

## Criterios

- Crear un puerto solo donde desacople una dependencia real o permita expresar el límite del caso de uso.
- No generar una interfaz por cada clase de forma automática.
- Los adaptadores traducen; el dominio decide.
- Los repositorios trabajan con conceptos/agregados del dominio, no filtran documentos crudos hacia Application.
