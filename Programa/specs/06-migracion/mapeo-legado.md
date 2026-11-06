# Mapeo del legado al nuevo dominio

> **Restricción R-01:** mapear el histórico sin perder trazabilidad. **Estrategia:** [ADR-005](../03-arquitectura/adr/ADR-005-estrategia-migracion.md). **Reglas:** REG-130 a REG-135. **Datos de prueba (FICTICIOS):** [`samples/legado/fichas-ejemplo.csv`](../../samples/legado/fichas-ejemplo.csv).
> **Formatos:** el destino principal del legado es el **12.1**, según [`Git/FORMATO_12_1.pdf`](../../../Git/FORMATO_12_1.pdf) (cabecera a–g, detalle a–i; ver `registro-inventario-12-1.schema.yaml`, `x-item-121`). Para el 14.1 y el 8.1 hay estructura PLE (comunitaria) y el formato impreso `Git/234_formato141.pdf`. ⚠ Las **tablas 5, 6 y 12** que exige el 12.1 **no** están en el workspace (PENDIENTE).

## 1. Origen: la ficha de almacén

| Campo legado | Contenido observado o supuesto | Schema crudo |
|---|---|---|
| `fecha` | Texto; formato habitual `dd/mm/aaaa`, con variantes (SUP) | `ficha-legado.schema.yaml#/properties/fecha` |
| `ingreso` | Cantidad que entra (texto; puede venir vacío o no ser numérico) | `#/properties/ingreso` |
| `salida` | Cantidad que sale | `#/properties/salida` |
| `producto` | Texto libre: a veces "CÓDIGO DESCRIPCIÓN", a veces solo la descripción | `#/properties/producto` |
| `nro_documento` | Documento interno informal (nota de ingreso, vale de salida…), **no** es una serie-número SUNAT (SUP-07) | `#/properties/nro_documento` |

## 2. Mapeo campo por campo

| Campo legado | Dominio nuevo | 12.1 (ítem de `FORMATO_12_1.pdf` → propiedad) | 14.1 Ventas | 8.1 Compras | Brecha | Estrategia |
|---|---|---|---|---|---|---|
| `fecha` | `MovimientoAlmacen.fecha` (yyyy-mm-dd) | **det-a** Fecha → `movimientos[].fecha` | — (las fichas no son ventas) | — | Formatos mixtos y fechas imposibles (31/02, mes 13) | Se normaliza a ISO. Si no se puede interpretar sin ambigüedad, va a **cuarentena** (REG-130). Nunca se inventa una fecha |
| `ingreso` | `MovimientoAlmacen{tipo: INGRESO, cantidad}` | **det-f** Entradas en unidades → `movimientos[].entradas` | — | Posible indicio de compra, **sin importes ni proveedor** | No hay unidad de medida, el valor no es numérico o es negativo | Se interpreta como decimal; si es ≤ 0 o no numérico, va a cuarentena (REG-135). La unidad se toma del producto homologado (si no, `NIU` provisional + advertencia) |
| `salida` | `MovimientoAlmacen{tipo: SALIDA, cantidad}` | **det-g** Salidas en unidades → `movimientos[].salidas` | Posible indicio de venta, **sin precio ni comprobante** | — | Igual que `ingreso` | Igual que `ingreso` |
| `ingreso` y `salida` a la vez | Dos movimientos con el mismo `origen.fila` | Entrada y salida el mismo día | — | — | Ambigüedad (¿ajuste? ¿transferencia?) | Se divide en dos movimientos y se marca con advertencia, o va a cuarentena según la configuración (REG-131) |
| `producto` | `Producto.codigoInterno` + `Producto.nombre` (MT-070, MT-069) | **cab-e** Código de la existencia → `existencias[].codigoExistencia`; **cab-f** Descripción → `descripcion`; **cab-g** Unidad → `unidadMedida` (Tabla 6 PENDIENTE) | — | — | **No hay código estandarizado de existencia** ni código de producto SUNAT (MT-071), ni unidad (MT-050), ni sistema de ISC (MT-065) | Si el texto empieza con un código (`^[A-Z]{3}-\w+`), se usa como código interno. Si no, se crea un **código provisional** `LEG-<hash>` con `requiereHomologacion = true` (REG-132). La homologación se hace en CU-13 |
| `nro_documento` | `MovimientoAlmacen.documentoInternoLegado` (relacionado con MT-018) | **det-b** Tipo (Tabla 10) → `tipoDocumento` = `00` Otros (SUPUESTO: documento interno); **det-c/det-d** Serie y número → `serie`/`numero` (se separa el prefijo, p. ej. `NI` / `0001`) | — | — | No es un comprobante SUNAT. Puede venir **repetido** o vacío | Se conserva literal. Los repetidos **no se fusionan**: cada fila es un movimiento distinto y se reporta (REG-133). Si viene vacío: advertencia |
| (la fila completa) | `Origen{fuente: LEGADO, archivo, fila, hashFila, loteImportacion}` | `movimientos[].origen` | — | — | — | **Trazabilidad**: el staging inmutable conserva la fila cruda y su SHA-256 (REG-134) |

## 3. Brechas y cómo se cierran

| ID | Brecha | Impacto | Cierre |
|---|---|---|---|
| BR-01 | El producto no tiene un código estandarizado de existencia | El 12.1 exige el código de la existencia según la Tabla 5 (cab-e, DISC-23) | Códigos provisionales y homologación manual (CU-13). Se mapean al código de existencia del 12.1 cuando la tabla oficial esté disponible (PENDIENTE) |
| BR-02 | No hay unidad de medida | El 12.1 y el UBL (MT-050) la exigen | Se toma de la unidad del producto homologado (catálogo 03) |
| BR-03 | No hay importes (valor ni precio) | Las fichas **no** pueden alimentar el 14.1 ni el 8.1 (SUP-08) ni un kardex valorizado | Solo se migran unidades físicas. Si se requiere un 13.1 valorizado, queda fuera de alcance |
| BR-04 | `nro_documento` informal y repetido | No hay vínculo con comprobantes SUNAT | Se conserva como referencia. **No** se fabrican comprobantes a partir del legado (ADR-005) |
| BR-05 | No hay establecimiento por ficha | El 12.1 se lleva por establecimiento | El lote se importa indicando el establecimiento (`?establecimiento=` en `importarLegado`) |
| BR-06 | No hay tipo de operación del 12.1 (det-e, Tabla 12) | El 12.1 lo exige | Se infiere solo por prefijo del documento (NI = ingreso, VS = venta, AJ = ajuste) como **sugerencia** con advertencia. La tabla oficial queda PENDIENTE |
| BR-07 | Calidad de fechas | Riesgo de movimientos fuera de período | Cuarentena (REG-130) |
| BR-08 | Puede haber saldos negativos | Inconsistencia física | Se reporta una advertencia y no se bloquea (REG-135); se concilia con un inventario físico inicial |
| BR-09 | No hay saldo inicial explícito | El 12.1 pide el saldo inicial en la columna de entradas (det-f, REG-148) | Primera migración: el saldo inicial es 0 o sale de un inventario físico de apertura que se carga como primera entrada del período (decisión del cliente, PENDIENTE) |

## 4. Clasificación esperada de `fichas-ejemplo.csv` (30 filas ficticias)

| Fila (sin encabezado) | Caso | Resultado esperado | Regla |
|---|---|---|---|
| 9 | Fecha `31/02/2024` (no existe) | Cuarentena | REG-130 |
| 13 | Fecha vacía | Cuarentena | REG-130 |
| 25 | Fecha `14/13/2024` (mes 13) | Cuarentena | REG-130 |
| 21 | Fecha `2024-01-12` (otro formato, pero sin ambigüedad) | Se migra con advertencia de formato | REG-130 |
| 10, 26 | Ingreso y salida a la vez | Se divide en 2 movimientos y se marca con advertencia | REG-131 |
| 14, 22 | Producto sin código (`arroz extra`, `detergente`) | Producto provisional `LEG-…` | REG-132 |
| 16 y 17 | `VS-0007` duplicado con datos idénticos | Ambos se migran y se reporta el posible duplicado | REG-133 |
| 7 y 8, 28 y 29 | El mismo `nro_documento` con productos o tipos distintos (`VS-0004`; `NI-0012` como ingreso y como salida) | Se migran y se reportan | REG-133 |
| 18 | Ingreso `diez` (no numérico) | Cuarentena | REG-135 |
| 19 | Salida `-4` (negativa) | Cuarentena | REG-135 |
| 23 | `nro_documento` vacío | Se migra con advertencia | REG-133 |
| 24 | Sin ingreso ni salida | Cuarentena | REG-135 |
| 30 | La salida de 200 deja el saldo negativo | Se migra y se advierte del saldo negativo | REG-135 |
| Resto | Filas limpias | Se migran | — |

**Conciliación esperada** con la política por defecto (dividir según REG-131 y aceptar la fila 21 con advertencia): 30 filas leídas = **6 en cuarentena** (filas 9, 13, 18, 19, 24 y 25) + **24 migradas**. Como 2 de ellas se dividen (filas 10 y 26), se crean **26 movimientos**. Se cumple `filasLeidas (30) = filas migradas (24) + filasEnCuarentena (6)`, y `movimientosCreados = 24 + 2`.
