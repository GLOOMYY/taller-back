# Compras

**Fase:** 3 · **Estado del módulo:** Confirmado para roadmap; dominio pendiente

## Propósito

Incorporar Compras en la fase 3 (RF-COM-001).

## Responsabilidades

El proceso y su efecto están **Pendientes**; no se asume un flujo de adquisición concreto.

## Qué NO pertenece

Estado propietario de Proveedores o Inventario, pagos a proveedores, impuestos, recepciones o devoluciones no confirmadas.

## Entidades/conceptos conocidos

Compra. Sus líneas, estados, documentos y relaciones están **Pendientes**.

## Reglas de negocio confirmadas

BR-007 aplica a las Compras del Taller. No existen reglas específicas confirmadas.

## Casos de uso candidatos

**Candidatos:** registrar, recibir, consultar o cancelar una Compra. Todos requieren definición previa.

## Dependencias permitidas/prohibidas

La colaboración futura con Proveedores e Inventario usará contratos; no modifica directamente sus colecciones.

## Consideraciones multi-tenant

Toda Compra operativa queda scoped al Taller y sus referencias deberán validar el mismo contexto.

## Preguntas/decisiones pendientes

Ciclo de vida, numeración, proveedor, líneas, moneda, costos, recepción, efecto en inventario, impuestos y anulaciones.
