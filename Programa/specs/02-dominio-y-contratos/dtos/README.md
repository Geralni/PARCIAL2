# DTOs: esqueletos en Kotlin (sin lógica)

- **Lenguaje:** Kotlin, según ADR-003 (Kotlin + Compose Multiplatform, con un módulo `shared` común para Windows y Android).
- **Fuente de verdad:** los JSON Schema de [`../schemas/`](../schemas/). Estos DTOs son su espejo tipado para el módulo `shared/domain` y `shared/application`.
- **Sin lógica:** no hay cálculos, validaciones ni `init {}` con código. Donde corresponde una regla se deja `// TODO(spec: REG-XXX)`.
- **Trazabilidad:** cada propiedad lleva un comentario `// MT-xxx` (fila de la [matriz](../../05-trazabilidad/matriz-trazabilidad.md)) o `// interno`.
- **Montos:** son `String` decimales en los DTOs y en el contrato. En el dominio se usará un tipo decimal exacto (por ejemplo, `BigDecimal` en la JVM o una librería multiplataforma). Nunca `Double`.
- **Paquetes** = contextos delimitados = futuros microservicios: `emision`, `integracion`, `inventario`, `migracion`, `registros`, `comun`.

| Archivo | Schemas que refleja |
|---|---|
| `comun/ValueObjects.kt` | `common.schema.yaml` y `catalogos.schema.yaml` |
| `emision/Comprobante.kt` | `comprobante`, `nota`, `linea-detalle`, `tributo`, `totales`, `forma-pago`, `adquirente`, `serie` |
| `emision/Emisor.kt` | `emisor`, `establecimiento`, `firma-digital`, `parametro-tributario` |
| `integracion/Integracion.kt` | `respuesta-sunat`, `comunicacion-baja`, `resumen-diario`, `validacion-ruc`, `problema` |
| `inventario/Inventario.kt` | `producto`, `movimiento-almacen` |
| `migracion/Migracion.kt` | `ficha-legado`, `importacion-legado` |
| `registros/Registros.kt` | `registro-ventas-14-1`, `registro-compras-8-1`, `registro-inventario-12-1` |
