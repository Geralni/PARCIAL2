# Índice de catálogos SUNAT (Anexo 8)

> ⚠ **Advertencia de fuente.** Los 14 catálogos provienen de `Git/NN.txt`, una fuente **comunitaria no oficial** cuya última actualización es de 2020. Se usan como semilla del contrato y **deben contrastarse con el Anexo 8 oficial de SUNAT** antes de pasar a producción (RSK-02).
> **Generados por** `tools/convertir_catalogos.py`, que detecta el formato, valida y normaliza. Todos los `.txt` resultaron ser **JSON** válido (una lista de objetos); ninguno era CSV.
> **Estructura de cada archivo:** `catNN.json` = `{numero, nombre, fuente, advertencia, campo_ubl[], contraste_anexo_9a, items[]}`, validada por [`../schemas/catalogo.schema.yaml`](../schemas/catalogo.schema.yaml).
> **Nota sobre el tipo de operación:** con UBL 2.1 se usa el catálogo **51**, no el 17. El Anexo 9-A (2017) lo ubica en `cbc:ProfileID`, pero la **validación SUNAT vigente** lo lee de **`cbc:InvoiceTypeCode/@listID`** (error 3206; MT-087). DISC-01 y DISC-06 quedan cerradas.

| N° | Nombre | Campo UBL destino (Anexo 9-A, RS 117-2017) | Págs. | Ítems | Contraste con el Anexo 9-A | Archivo |
|---|---|---|---|---|---|---|
| 01 | Tipo de documento | `/Invoice/cbc:InvoiceTypeCode`; `cbc:DocumentTypeCode` en referencias, RC y RA | 1, 19, 28, 31 | 40 | ⚠ **DISCREPANCIA**: la boleta figura como `"02"` en la pág. 11, pero el catálogo la tiene como `03` (DISC-04) | [cat01.json](cat01.json) |
| 02 | Tipo de moneda | `cbc:DocumentCurrencyCode`; `@currencyID` de todos los montos | 1, 7 | 179 (deduplicado de 279 filas país-moneda) | No aplica: el anexo remite a ISO 4217 | [cat02.json](cat02.json) |
| 03 | Unidad de medida | `cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode` | 8 | 62 | No aplica: el anexo remite a UN/ECE rec 20 | [cat03.json](cat03.json) |
| 04 | País | `cac:Country/cbc:IdentificationCode` | 6 | 240 | No aplica: el anexo remite a ISO 3166-1, y se usa el código alfa-2 | [cat04.json](cat04.json) |
| 05 | Tipos de tributos | `cac:TaxScheme/cbc:ID`, `cbc:Name`, `cbc:TaxTypeCode` | 7, 10, 20, 29 | 10 | ⚠ **DISCREPANCIA**: en la factura la longitud de ID y TaxTypeCode aparece invertida respecto de la NC y el RC (DISC-05). El código 7152 (ICBPER) no tiene respaldo en el anexo: **PENDIENTE** | [cat05.json](cat05.json) |
| 06 | Documento de identidad | `cbc:CompanyID/@schemeID` (emisor, adquirente) | 3 | 10 | ✅ Coherente (an1) | [cat06.json](cat06.json) |
| 07 | Afectación del IGV | `cac:TaxCategory/cbc:TaxExemptionReasonCode` (línea) | 10 | 19 | ✅ Coherente (an2). La relación con el catálogo 05 (`codigo_de_tributo`) solo tiene respaldo en la fuente comunitaria | [cat07.json](cat07.json) |
| **08** | **Sistema de cálculo del ISC** | `cac:TaxCategory/cbc:TierRange` (línea) | 10, 17, 22, 26 | 3 | ✅ Coherente (0..1, an2). Las tasas y los montos del ISC: **PENDIENTE** | [cat08.json](cat08.json) |
| 09 | Tipo de nota de crédito | `/CreditNote/cac:DiscrepancyResponse/cbc:ResponseCode` | 19 | 13 | ⚠ PARCIAL: el código 13 (cuotas) no tiene respaldo en el anexo (**PENDIENTE**) | [cat09.json](cat09.json) |
| 10 | Tipo de nota de débito | `/DebitNote/cac:DiscrepancyResponse/cbc:ResponseCode` | 23 | 5 | ✅ Coherente (n2) | [cat10.json](cat10.json) |
| 16 | Tipo de precio | `cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode` | 8 | 3 | ✅ Coherente (an2) | [cat16.json](cat16.json) |
| **51** | **Tipo de operación** | `/Invoice/cbc:ProfileID` | 1, 11 | 28 | ⚠ **DISCREPANCIA**: el anexo dice `an2`, pero los códigos tienen 4 dígitos (DISC-06), y el `@schemeURI` termina en `catalogo17` (DISC-01) | [cat51.json](cat51.json) |
| 52 | Leyendas | `cbc:Note/@languageLocaleID` | 1 | 14 | ✅ Coherente (n4) | [cat52.json](cat52.json) |
| 53 | Cargos y descuentos | `cac:AllowanceCharge/cbc:AllowanceChargeReasonCode` (global y por línea) | 6, 9 | 21 | ✅ Coherente (an2) | [cat53.json](cat53.json) |

## Cómo se contrastaron los catálogos 05, 07, 08 y 51

El Anexo 9-A **no contiene las tablas de los catálogos**; esas tablas están en el Anexo 8, que no está en el workspace. El contraste posible fue **estructural**: se verificó que el formato y la longitud declarados por el Anexo 9-A para el nodo destino sean compatibles con los códigos del catálogo, y que el nodo cite el catálogo correcto. El contraste de **contenido** (que la lista de códigos sea exacta y esté vigente) queda **PENDIENTE** del Anexo 8 oficial.

## Catálogos citados por el Anexo 9-A que no están en el workspace (PENDIENTE)

12 (documentos relacionados), 13 (ubigeo), 18 (modalidad de traslado), 19 (estado del ítem en el resumen diario, pág. 29), 20 (motivo de traslado), 24, 54 (detracción), 55, 56, 57 y 58. También el catálogo **11**, que el resumen diario cita en la pág. 29 como "Tipo de afectación de IGV - Catálogo No 11", aunque en la factura esa afectación usa el **07**: es la discrepancia DISC-09.
