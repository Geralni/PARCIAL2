# Matriz de trazabilidad de registros PLE (14.1 y 8.1)

> **GENERADO** por `tools/construir_matriz.py` y verificado por `tools/verificar_matriz.py` (M10).
> **Fuente:** estructura PLE transcrita en `Git/Macro excel Registro de compras y ventas excel 2019 MOD.xlsm` (plantilla **comunitaria**; ver `referencias/formatos/README.md`).
> La columna **MT** enlaza con la [matriz del Anexo 9-A](matriz-trazabilidad.md). 'interno' significa que el dato no sale del comprobante UBL emitido (por ejemplo, el CUO contable o las compras recibidas).

## Formato 14.1 → `registro-ventas-14-1.schema.yaml`

| Campo PLE | Descripción (PLE) | Long. | Oblig. | Propiedad del schema | MT |
|---|---|---|---|---|---|
| 1 | Periodo | 8 | Si | `periodo` | interno |
| 2 | 1. Contribuyentes del Régimen General: Número correlativo del mes o Código Único de la Operación (CUO), que es… | Hasta 40 | Si | `cuo` | interno |
| 3 | Número correlativo del asiento contable identificado en el campo 2, cuando se utilice el Código Único de la Op… | De 2 hasta 10 | Si | `correlativoAsiento` | interno |
| 4 | Fecha de emisión del Comprobante de Pago | 10 | No | `fechaEmision` | MT-007 |
| 5 | Fecha de Vencimiento o Fecha de Pago (1) | 10 | No | `fechaVencimiento` | MT-009 |
| 6 | Tipo de Comprobante de Pago o Documento | 2 | Si | `tipoComprobante` | MT-010 |
| 7 | Número serie del comprobante de pago o documento o número de serie de la maquina registradora | Hasta 20 | Si | `serie` | MT-006 |
| 8 | Número del comprobante de pago o documento. Para efectos del registro de tickets o cintas emitidos por máquina… | Hasta 20 | Si | `numero` | MT-006 |
| 9 | 1. Para efectos del registro de tickets o cintas emitidos por máquinas registradoras que no otorguen derecho a… | Hasta 20 | No | `numeroFinalConsolidado` | interno |
| 10 | Tipo de Documento de Identidad del cliente | 1 | No | `clienteTipoDocumento` | MT-079 |
| 11 | Número de Documento de Identidad del cliente | Hasta 15 | No | `clienteNumeroDocumento` | MT-078 |
| 12 | Apellidos y nombres, denominación o razón social del cliente. En caso de personas naturales se debe consignar … | Hasta 100 | No | `clienteRazonSocial` | MT-088 |
| 13 | Valor facturado de la exportación | Hasta 12 enteros y h | No | `valorExportacion` | MT-035 |
| 14 | Base imponible de la operación gravada (4) | Hasta 12 enteros y h | No | `baseImponibleGravada` | MT-035 |
| 15 | Descuento de la Base Imponible | Hasta 12 enteros y h | No | `descuentoBaseImponible` | MT-043 |
| 16 | Impuesto General a las Ventas y/o Impuesto de Promoción Municipal | Hasta 12 enteros y h | No | `igvIpm` | MT-036 |
| 17 | Descuento del Impuesto General a las Ventas y/o Impuesto de Promoción Municipal | Hasta 12 enteros y h | No | `descuentoIgvIpm` | interno |
| 18 | Importe total de la operación exonerada | Hasta 12 enteros y h | No | `exonerado` | MT-035 |
| 19 | Importe total de la operación inafecta | Hasta 12 enteros y h | No | `inafecto` | MT-035 |
| 20 | Impuesto Selectivo al Consumo, de ser el caso. | Hasta 12 enteros y h | No | `isc` | MT-036 |
| 21 | Base imponible de la operación gravada con el Impuesto a las Ventas del Arroz Pilado | Hasta 12 enteros y h | No | `baseImponibleIvap` | MT-035 |
| 22 | Impuesto a las Ventas del Arroz Pilado | Hasta 12 enteros y h | No | `ivap` | MT-036 |
| 23 | Impuesto al Consumo de las Bolsas de Plástico. | Hasta 12 enteros y h | No | `icbper` | MT-190 |
| 24 | Otros conceptos, tributos y cargos que no forman parte de la base imponible | Hasta 12 enteros y h | No | `otrosTributosCargos` | MT-044 |
| 25 | Importe total del comprobante de pago | Hasta 12 enteros y h | No | `importeTotal` | MT-046 |
| 26 | Código de la Moneda (Tabla 4) | 3 | No | `moneda` | MT-013 |
| 27 | Tipo de cambio (5) | 1 entero y 3 decimal | No | `tipoCambio` | interno |
| 28 | Fecha de emisión del comprobante de pago o documento original que se modifica (6) o documento referencial al d… | 10 | No | `documentoModificadoFecha` | interno |
| 29 | Tipo del comprobante de pago que se modifica (6) | 2 | No | `documentoModificadoTipo` | MT-100 |
| 30 | Número de serie del comprobante de pago que se modifica (6) o Código de la Dependencia Aduanera | Hasta 20 | No | `documentoModificadoSerie` | MT-099 |
| 31 | Número del comprobante de pago que se modifica (6) o Número de la DUA, de corresponder | Hasta 20 | No | `documentoModificadoNumero` | MT-099 |
| 32 | Identificación del Contrato o del proyecto en el caso de los Operadores de las sociedades irregulares, consorc… | 12 | No | `contratoProyecto` | interno |
| 33 | Error tipo 1: inconsistencia en el tipo de cambio | 1 | No | `errorTipoCambio` | interno |
| 34 | Indicador de Comprobantes de pago cancelados con medios de pago | 1 | No | `indicadorMediosPago` | interno |
| 35 | Estado que identifica la oportunidad de la anotación o indicación si ésta corresponde a alguna de las situacio… | 1 | Si | `estadoAnotacion` | interno |
| 36 al 70 | Campos de libre utilización. | Hasta 200 | No | `— (campos de libre uso; no se modelan)` |  |

## Formato 8.1 → `registro-compras-8-1.schema.yaml`

| Campo PLE | Descripción (PLE) | Long. | Oblig. | Propiedad del schema | MT |
|---|---|---|---|---|---|
| 1 | Periodo | 8 | Si | `periodo` | interno |
| 2 | 1. Contribuyentes del Régimen General: Número correlativo del mes o Código Único de la Operación (CUO), que es… | Hasta 40 | Si | `cuo` | interno |
| 3 | Número correlativo del asiento contable identificado en el campo 2, cuando se utilice el Código Único de la Op… | De 2 hasta 10 | Si | `correlativoAsiento` | interno |
| 4 | Fecha de emisión del comprobante de pago o documento | 10 | Si | `fechaEmision` | interno |
| 5 | Fecha de Vencimiento o Fecha de Pago (1) | 10 | No | `fechaVencimientoPago` | interno |
| 6 | Tipo de Comprobante de Pago o Documento | 2 | Si | `tipoComprobante` | interno |
| 7 | Serie del comprobante de pago o documento. En los casos de la Declaración Única de Aduanas (DUA) o de la Decla… | Hasta 20 | No | `serie` | interno |
| 8 | Año de emisión de la DUA o DSI | 4 | No | `anioDua` | interno |
| 9 | Número del comprobante de pago o documento o número de orden del formulario físico o virtual donde conste el p… | Hasta 20 | Si | `numero` | interno |
| 10 | En caso de optar por anotar el importe total de las operaciones diarias que no otorguen derecho a crédito fisc… | Hasta 20 | No | `numeroFinalConsolidado` | interno |
| 11 | Tipo de Documento de Identidad del proveedor | 1 | No | `proveedorTipoDocumento` | interno |
| 12 | Número de RUC del proveedor o número de documento de Identidad, según corresponda. | Hasta 15 | No | `proveedorNumeroDocumento` | interno |
| 13 | Apellidos y nombres, denominación o razón social del proveedor. En caso de personas naturales se debe consigna… | Hasta 100 | No | `proveedorRazonSocial` | interno |
| 14 | Base imponible de las adquisiciones gravadas que dan derecho a crédito fiscal y/o saldo a favor por exportació… | Hasta 12 enteros y h | No | `baseGravadaDestinoGravado` | interno |
| 15 | Monto del Impuesto General a las Ventas y/o Impuesto de Promoción Municipal | Hasta 12 enteros y h | No | `igvDestinoGravado` | interno |
| 16 | Base imponible de las adquisiciones gravadas que dan derecho a crédito fiscal y/o saldo a favor por exportació… | Hasta 12 enteros y h | No | `baseGravadaDestinoMixto` | interno |
| 17 | Monto del Impuesto General a las Ventas y/o Impuesto de Promoción Municipal | Hasta 12 enteros y h | No | `igvDestinoMixto` | interno |
| 18 | Base imponible de las adquisiciones gravadas que no dan derecho a crédito fiscal y/o saldo a favor por exporta… | Hasta 12 enteros y h | No | `baseGravadaSinCredito` | interno |
| 19 | Monto del Impuesto General a las Ventas y/o Impuesto de Promoción Municipal | Hasta 12 enteros y h | No | `igvSinCredito` | interno |
| 20 | Valor de las adquisiciones no gravadas | Hasta 12 enteros y h | No | `adquisicionesNoGravadas` | interno |
| 21 | Monto del Impuesto Selectivo al Consumo en los casos en que el sujeto pueda utilizarlo como deducción. | Hasta 12 enteros y h | No | `isc` | interno |
| 22 | Impuesto al Consumo de las Bolsas de Plástico. | Hasta 12 enteros y h | No | `icbper` | interno |
| 23 | Otros conceptos, tributos y cargos que no formen parte de la base imponible. | Hasta 12 enteros y h | No | `otrosTributosCargos` | interno |
| 24 | Importe total de las adquisiciones registradas según comprobante de pago. | Hasta 12 enteros y h | Si | `importeTotal` | interno |
| 25 | Código de la Moneda (Tabla 4) | 3 | No | `moneda` | interno |
| 26 | Tipo de cambio (3). | 1 entero y 3 decimal | No | `tipoCambio` | interno |
| 27 | Fecha de emisión del comprobante de pago que se modifica (4). | 10 | No | `documentoModificadoFecha` | interno |
| 28 | Tipo de comprobante de pago que se modifica (4). | 2 | No | `documentoModificadoTipo` | interno |
| 29 | Número de serie del comprobante de pago que se modifica (4). | Hasta 20 | No | `documentoModificadoSerie` | interno |
| 30 | Código de la dependencia Aduanera de la Declaración Única de Aduanas (DUA) o de la Declaración Simplificada de… | 3 | No | `codigoDependenciaAduanera` | interno |
| 31 | Número del comprobante de pago que se modifica (4). | Hasta 20 | No | `documentoModificadoNumero` | interno |
| 32 | Fecha de emisión de la Constancia de Depósito de Detracción (5) | 10 | No | `detraccionFecha` | interno |
| 33 | Número de la Constancia de Depósito de Detracción (5) | Hasta 24 | No | `detraccionNumero` | interno |
| 34 | Marca del comprobante de pago sujeto a retención | 1 | No | `marcaRetencion` | interno |
| 35 | Clasificación de los bienes y servicios adquiridos (Tabla 30) Aplicable solo a los contribuyentes que hayan ob… | 1 | No | `clasificacionBienesServicios` | interno |
| 36 | Identificación del Contrato o del proyecto en el caso de los Operadores de las sociedades irregulares, consorc… | 12 | No | `contratoProyecto` | interno |
| 37 | Error tipo 1: inconsistencia en el tipo de cambio | 1 | No | `errorTipo1` | interno |
| 38 | Error tipo 2: inconsistencia por proveedores no habidos | 1 | No | `errorTipo2` | interno |
| 39 | Error tipo 3: inconsistencia por proveedores que renunciaron a la exoneración del Apéndice I del IGV | 1 | No | `errorTipo3` | interno |
| 40 | Error tipo 4: inconsistencia por DNIs que fueron utilizados en las Liquidaciones de Compra y que ya cuentan co… | 1 | No | `errorTipo4` | interno |
| 41 | Indicador de Comprobantes de pago cancelados con medios de pago | 1 | No | `indicadorMediosPago` | interno |
| 42 | Estado que identifica la oportunidad de la anotación o indicación si ésta corresponde a un ajuste. | 1 | Si | `estadoAnotacion` | interno |
| 43 al 84 | Campos de libre utilización. | Hasta 200 | No | `— (campos de libre uso; no se modelan)` |  |

## Formato 12.1 → `registro-inventario-12-1.schema.yaml`

> Fuente: `Git/FORMATO_12_1.pdf` (los ítems no son campos PLE numerados). Las tablas 5, 6 y 12 están PENDIENTE.

| Ítem | Texto del formato | Propiedad(es) del schema (MT o interno) | Origen en el legado |
|---|---|---|---|
| cab-a | Denominación del libro o registro. | `denominacion (interno)` | — (constante) |
| cab-b | Período y/o ejercicio al que corresponde la información registrada. | `periodo (interno)` | derivado de `fecha` (AAAAMM) |
| cab-c | Número de RUC del deudor tributario, Apellidos y Nombres, Denominación y/o Razón Social de este. | `ruc (MT-073)`; `razonSocial (MT-075)` | — (dato del emisor) |
| cab-d | Información del Establecimiento donde se ubican las existencias. | `establecimientoCodigo (MT-076)`; `establecimientoDescripcion (interno)` | parámetro `establecimiento` del lote (BR-05) |
| cab-e | Código de la existencia (según Tabla 5). | `existencias[].codigoExistencia (MT-070)` | `producto` (código al inicio, o provisional `LEG-<hash>`, REG-132) |
| cab-f | Descripción de la existencia. | `existencias[].descripcion (MT-069)` | `producto` (descripción) |
| cab-g | Código de la unidad de medida (según tabla 6). | `existencias[].unidadMedida (MT-050)` | — (brecha BR-02: del producto homologado) |
| det-a | Fecha de emisión del documento de traslado, comprobante de pago, documento interno o similar. | `existencias[].movimientos[].fecha (interno)` | `fecha` (REG-130) |
| det-b | Tipo de documento de traslado, comprobante de pago, documento interno o similar (según Tabla 10). | `existencias[].movimientos[].tipoDocumento (interno)` | `nro_documento` → '00' Otros (SUPUESTO) |
| det-c | Número de serie del documento de traslado, comprobante de pago, documento interno o similar. | `existencias[].movimientos[].serie (interno)` | `nro_documento` (prefijo, p. ej. NI/VS/AJ) |
| det-d | Número del documento de traslado, comprobante de pago, documento interno o similar. | `existencias[].movimientos[].numero (interno)` | `nro_documento` (número) |
| det-e | Tipo de operación (según Tabla 12). | `existencias[].movimientos[].tipoOperacion (interno)` | — (brecha BR-06: Tabla 12 PENDIENTE; sugerido por el prefijo) |
| det-f | Entradas en unidades, adicionalmente considerar en esta columna la información del saldo inicial. | `existencias[].movimientos[].entradas (interno)` | `ingreso` (REG-131, REG-135); saldo inicial: BR-09 |
| det-g | Salidas en unidades. | `existencias[].movimientos[].salidas (interno)` | `salida` (REG-131, REG-135) |
| det-h | Saldo final en unidades. | `existencias[].movimientos[].saldoFinal (interno)` | calculado (saldo acumulado) |
| det-i | Totales. | `existencias[].totales (interno)`; `existencias[].totales.entradas (interno)`; `existencias[].totales.salidas (interno)`; `existencias[].totales.saldoFinal (interno)` | calculado (REG-148) |
