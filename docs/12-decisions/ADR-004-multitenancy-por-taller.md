# ADR-004: Multi-tenancy por Taller

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

Usuarios pueden participar en varios Talleres y cada Taller debe mantener aislados sus Clientes y datos operativos.

## Decisión

Cada Taller es un tenant. Membresía vincula Usuario y Taller. Todo acceso operativo usa un contexto de Taller derivado y validado del lado confiable; no basta un `taller_id` enviado por el cliente. Persistencia, casos de uso, API y pruebas refuerzan el aislamiento.

## Consecuencias

- Toda ruta de datos requiere evaluación tenant.
- Las referencias cruzadas validan pertenencia.
- Un Cliente no se comparte entre Talleres.
- Pruebas negativas cross-tenant son obligatorias.
- Roles/permisos siguen pendientes y no alteran esta regla.

## No decidido

Estrategia física en MongoDB, operaciones globales y modelo exacto de autorización.
