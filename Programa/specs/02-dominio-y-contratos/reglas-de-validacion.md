# Reglas de validación

> **Fase 1, SPEC-FIRST.** Aquí se *especifica* cada regla; no se implementa. En los DTOs, cada regla aparece como `// TODO(spec: REG-XXX)`.
> **Origen:** la lista "lo que el XSD NO valida" ([mapa-xsd.md §3](mapa-xsd.md)), el Anexo 9-A (`Git/anexoIX-117-2017.pdf`), los catálogos ([catalogs/INDEX.md](catalogs/INDEX.md)) y las observaciones del DEMO de Nubefact.
> **Severidad:** `ERROR` bloquea la emisión o el envío. `ADVERTENCIA` permite continuar, pero queda registrada. `INFO` es solo informativa.
> **Estado de la fuente:** `CITADA` (la fuente está en el workspace), `SUPUESTO` (decisión de diseño que se debe confirmar) o `PENDIENTE` (falta la norma o el valor oficial; ver [00-analisis-del-caso.md §9](../00-analisis-del-caso.md)).
> **Validación SUNAT vigente (28/10):** `Git/XSL Actualizado al 06092022 (1)/validaciones` contiene las hojas XSL con las que SUNAT valida los CPE (3 378 reglas y 891 códigos de error, extraídos en `referencias/sunat-xsl/reglas-xsl.csv`). Donde una regla cita "XSL SUNAT", el respaldo es esa validación oficial, que prevalece sobre el Anexo 9-A de 2017. Los códigos de error por dato están en la columna `codigos_error_sunat` de la matriz.
> **Parámetros:** ninguna tasa ni valor vigente se fija aquí. Todos se leen del puerto `ParametrosTributariosPort` con vigencia `desde`/`hasta` (RNF-06).

## 1. Estructura y valores fijos (REG-001 a REG-009)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-001 | `cbc:UBLVersionID` = **"2.1"** en factura, boleta, NC y ND; **"2.0"** en el resumen diario y la baja. | XSL SUNAT 06/09/2022: Factura, Boleta, NC y ND (`^(2.1)$`, errores 2074/2075); Summary-1.1.0 y SummaryVoided-1.0.1 (`^(2.0)$`). El Anexo 9-A (2017) decía "2.0" en boleta y notas (DISC-12 cerrada) | ERROR | CITADA (validación SUNAT) |
| REG-002 | `cbc:CustomizationID` = **"2.0"** en factura, boleta, NC y ND; **"1.1"** en el resumen diario; **"1.0"** en la baja. | XSL SUNAT 06/09/2022: Factura, Boleta, NC y ND (`^(2.0)$`, errores 2072/2073); Summary-1.1.0 (`^(1.1)$`); SummaryVoided-1.0.1 (`^(1.0)$`) | ERROR | CITADA (validación SUNAT) |
| REG-003 | Campos obligatorios de cabecera: serie-número, fecha de emisión, emisor, adquirente, importe total y al menos una línea. | Anexo 9-A, págs. 1, 3, 7 y 8 (cardinalidad 1); XSD (`AccountingSupplierParty` 1..1, `LegalMonetaryTotal` 1..1, `InvoiceLine` 1..n) | ERROR | CITADA |
| REG-004 | `tipoComprobante` es **obligatorio en el contrato**, aunque el anexo y el XSD lo declaren 0..1, porque determina todas las demás reglas. | Anexo 9-A, pág. 1 (0..1) | ERROR | SUPUESTO |
| REG-005 | El número de orden del ítem es un entero de hasta 3 dígitos (`n..3`), único y consecutivo dentro del comprobante, empezando en 1. | Anexo 9-A, págs. 8, 21 y 26 (`n..3`). Lo de único y consecutivo es SUPUESTO | ERROR | CITADA / SUPUESTO |
| REG-006 | Un comprobante tiene **entre 1 y 999 líneas**. El límite superior se deriva de `n..3`. | Anexo 9-A, pág. 8; XSD `InvoiceLine` 1..n | ERROR | CITADA (derivada) |
| REG-007 | Una nota de crédito o débito **debe** tener `DiscrepancyResponse` y `BillingReference` (el anexo los marca 0..n, con hijos obligatorios). | Anexo 9-A, págs. 19 y 23 | ERROR | SUPUESTO (obligatoriedad del nodo) |
| REG-008 | Cada leyenda tiene un texto de hasta 100 caracteres y un código del catálogo 52. | Anexo 9-A, pág. 1 (`an..100`, `n4`) | ERROR | CITADA |
| REG-009 | Si se informa `LineCountNumeric`, debe ser igual al número de líneas. | Anexo 9-A, pág. 1 ("Cantidad de ítems") | ERROR | CITADA (derivada) |

## 2. Catálogos (REG-010 a REG-029)

Todas validan el código contra `catalogs/catNN.json`. Como la fuente es comunitaria (RSK-02), un código ausente produce `ERROR`, pero el catálogo cargado es un parámetro versionado.

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-010 | `tipoComprobante`, y todo tipo de documento referenciado, pertenece al catálogo 01 y es coherente con la raíz UBL: `01`/`03` → Invoice, `07` → CreditNote, `08` → DebitNote. | Catálogo 01; Anexo 9-A, págs. 1, 11, 19 y 23; DISC-04 (la boleta figura como "02" en el anexo) | ERROR | CITADA (con discrepancia) |
| REG-011 | La moneda pertenece al catálogo 02 (ISO 4217). | Anexo 9-A, pág. 1; catálogo 02 | ERROR | CITADA |
| REG-012 | La unidad de medida pertenece al catálogo 03. | Anexo 9-A, pág. 8; catálogo 03 | ERROR | CITADA |
| REG-013 | El código de país pertenece al catálogo 04 (ISO 3166-1 alfa-2). | Anexo 9-A, pág. 6; catálogo 04 | ERROR | CITADA |
| REG-014 | El código de tributo pertenece al catálogo 05. `Name` y `TaxTypeCode` se **derivan** del mismo ítem del catálogo, no se reciben del cliente. | Anexo 9-A, págs. 7 y 10; catálogo 05; DISC-05 | ERROR | CITADA (con discrepancia de longitudes) |
| REG-015 | El tipo de documento de identidad pertenece al catálogo 06. El del emisor siempre es "6". | Anexo 9-A, pág. 3; catálogo 06 | ERROR | CITADA |
| REG-016 | La afectación del IGV de cada línea pertenece al catálogo 07. | Anexo 9-A, pág. 10; catálogo 07 | ERROR | CITADA |
| REG-017 | El sistema de cálculo del ISC (`TierRange`) pertenece al catálogo 08. Se informa **si y solo si** la línea tiene el tributo ISC (2000). | Anexo 9-A, págs. 10, 17, 22 y 26; catálogo 08. La condición "si y solo si" es SUPUESTO | ERROR | CITADA / SUPUESTO |
| REG-018 | El código de tipo de nota de crédito pertenece al catálogo 09. | Anexo 9-A, pág. 19; catálogo 09 (el código 13 queda PENDIENTE, DISC-14) | ERROR | CITADA |
| REG-019 | El código de tipo de nota de débito pertenece al catálogo 10. | Anexo 9-A, pág. 23; catálogo 10 | ERROR | CITADA |
| REG-020 | El tipo de precio pertenece al catálogo 16. | Anexo 9-A, pág. 8; catálogo 16 | ERROR | CITADA |
| REG-021 | El tipo de operación pertenece al catálogo **51** (4 dígitos) y se informa en **`cbc:InvoiceTypeCode/@listID`** (MT-087). `cbc:ProfileID` (Anexo 9-A, 2017) ya no se valida. | XSL SUNAT 06/09/2022: ValidaExprRegFactura-2.0.1, líneas 107 y 911 (error 3206); Boleta, línea 92. Resuelve DISC-01 y DISC-06 | ERROR | CITADA (validación SUNAT) |
| REG-022 | La combinación afectación (07) ↔ tributo (05) debe estar en `cat07.items[].codigo_de_tributo`. Por ejemplo, 20 (exonerado) → 9997. | `Git/07.txt` (columna `codigo_de_tributo`, fuente **comunitaria**) | ADVERTENCIA | SUPUESTO (sin respaldo en el Anexo 9-A) |
| REG-023 | El tipo de operación (51) debe admitir el tipo de comprobante según `cat51.items[].tipo_de_comprobante_asociado`. | `Git/51.txt` (fuente comunitaria) | ADVERTENCIA | SUPUESTO |
| REG-024 | El código de cargo o descuento pertenece al catálogo 53. Su **nivel** (Item o Global) debe coincidir con la posición en el documento, y `ChargeIndicator` debe valer `false` para los "Descuentos…" y `true` para los "Cargos…". | Anexo 9-A, págs. 6 y 9; catálogo 53 (columna `nivel`) | ERROR | CITADA / SUPUESTO (la relación con el indicador) |
| REG-025 | El código de leyenda pertenece al catálogo 52 y no se repite dentro del comprobante. | Anexo 9-A, pág. 1; catálogo 52. Lo de no repetirse es SUPUESTO | ERROR | CITADA / SUPUESTO |
| REG-026 | El tipo de documento relacionado pertenece al catálogo 12. | Anexo 9-A, pág. 2 | ADVERTENCIA | PENDIENTE (el catálogo 12 no está en el workspace) |
| REG-027 | El código de producto SUNAT tiene 8 dígitos (`n8`, UNSPSC). | Anexo 9-A, pág. 10 | ERROR | CITADA |
| REG-028 | Forma de pago: `cac:PaymentTerms` con `cbc:ID = 'FormaPago'` y `cbc:PaymentMeansID` = `Contado` o `Credito`. Si es crédito, `cbc:Amount` es el monto neto pendiente. No puede haber Contado y Credito a la vez. | XSL SUNAT 06/09/2022: ValidaExprRegFactura-2.0.1, líneas 41, 524 y 1011–1071 (errores 3127–3129, 3245, 3246, 3248, entre otros) | ERROR | CITADA (validación SUNAT) / PENDIENTE (texto de los anexos 2019–2020) |
| REG-029 | Cuotas: `cac:PaymentTerms` con `PaymentMeansID = 'Cuota###'`, `cbc:Amount` y `cbc:PaymentDueDate`. La suma de las cuotas debe ser igual al monto neto pendiente. | XSL SUNAT 06/09/2022: ValidaExprRegFactura-2.0.1, líneas 1064–1067 (suma de cuotas frente a pendiente) | ERROR | CITADA (validación SUNAT) |

## 3. Series, correlativos y establecimiento (REG-030 a REG-039)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-030 | Formato del identificador de una factura y sus notas: `F` + 3 caracteres alfanuméricos, guion y correlativo de hasta 8 dígitos (`F###-NNNNNNNN`). | Anexo 9-A, págs. 1, 19 y 23 | ERROR | CITADA |
| REG-031 | Formato de la boleta: `^([B][A-Z0-9]{3}\|[0-9]{4})-[0-9]{1,8}$` (serie B### o de contingencia NNNN). Las notas admiten `F`, `B` o `S`. | XSL SUNAT 06/09/2022: ValidaExprRegBoleta-2.0.1, línea 139; ValidaExprRegNC-2.0.1, línea 207. Resuelve DISC-13 | ERROR | CITADA (validación SUNAT) |
| REG-032 | Una nota usa una serie con la **misma letra** que el comprobante que modifica (F → F, B → B). | ENT-06 §6; manual Nubefact (`serie`) | ERROR | SUPUESTO (fuente de mercado) |
| REG-033 | Serie de contingencia: 4 dígitos numéricos (`NNNN-NNNNNNNN`), admitida en factura, boleta y notas. Solo se usa en modo contingencia o sin conexión. | XSL SUNAT 06/09/2022: Factura línea 155, Boleta línea 139, NC línea 207 (`[0-9]{4}`); Anexo 9-A, págs. 2, 6 y 19 | ERROR | CITADA (formato) / PENDIENTE (condiciones de uso) |
| REG-034 | Unicidad: no existen dos comprobantes con el mismo emisor + tipo + serie + correlativo. | Integridad del correlativo; manual Nubefact, error 23 "Este documento ya existe" | ERROR | SUPUESTO |
| REG-035 | El correlativo es consecutivo por serie (el siguiente es el último + 1), lo asigna el sistema (ENT-06 §2, "Número (Referencial)") y no se reutiliza. | ENT-06 §2 | ERROR | SUPUESTO (PENDIENTE de norma) |
| REG-036 | El código de establecimiento tiene 4 dígitos, va en `cac:PartyLegalEntity/cac:RegistrationAddress/cbc:AddressTypeCode` (MT-076) y corresponde a un establecimiento registrado del emisor. | XSL SUNAT 06/09/2022: Factura y Boleta (template cac:AccountingSupplierParty; errores 3030, 3239, 4198, 4199, 4242); Anexo 9-A, pág. 3 (`n4`) | ERROR | CITADA (validación SUNAT) |
| REG-037 | Una serie pertenece a un único establecimiento y a un tipo de comprobante (o grupo comprobante + notas). | ENT-06 §6 | ERROR | SUPUESTO |
| REG-038 | El ubigeo tiene 6 dígitos (catálogo 13) y va en `cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID` del emisor (MT-077). | XSL SUNAT 06/09/2022: Factura y Boleta (error 4093). DISC-24 cerrada. El catálogo 13 no está en el workspace | ERROR (formato) / ADVERTENCIA (catálogo) | CITADA (ubicación y formato) / PENDIENTE (catálogo 13) |

## 4. Identidad: RUC y documentos (REG-040 a REG-049)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-040 | El RUC tiene exactamente 11 dígitos numéricos. | Anexo 9-A, pág. 3 (`CompanyID n11`); catálogo 06 (código 6) | ERROR | CITADA |
| REG-041 | El dígito verificador del RUC es válido. Se usa un algoritmo de módulo 11, pero su especificación oficial **no está en el workspace**. | — | ADVERTENCIA (pasará a ERROR cuando haya fuente) | **PENDIENTE** (P-8) |
| REG-042 | `schemeID = "6"` implica un número de 11 dígitos que cumple REG-040. | Anexo 9-A, pág. 3; catálogo 06 | ERROR | CITADA |
| REG-043 | `schemeID = "1"` (DNI) implica 8 dígitos. Las longitudes de los demás tipos (4, 7, A–E) no están definidas. | — | ADVERTENCIA | PENDIENTE (las longitudes no figuran en el workspace) |
| REG-044 | En una **factura**, el adquirente se identifica con RUC, salvo las operaciones de exportación o con no domiciliados (catálogo 51: 0200–0208, 0401). | — | ERROR | PENDIENTE (norma de comprobantes no disponible) |
| REG-045 | En una **boleta** se admite el cliente genérico "VARIOS" (sin documento) por debajo de un monto umbral. El umbral es un parámetro (`UMBRAL_BOLETA_SIN_DOCUMENTO`). | ENT-06 §2 (cliente "VARIOS"). La estructura PLE 14.1 (campos 10 y 11) hace opcional el documento del cliente cuando "campo 25 < 700.00 y campo 6 = '03'" (fuente comunitaria). La norma de comprobantes no está en el workspace | ADVERTENCIA | CITADA (comunitaria) / PENDIENTE (norma) |
| REG-046 | La validación de RUC contra el padrón SUNAT (estado y condición) se hace a través del puerto `ValidadorRucPort`, y su resultado se guarda con su fecha. | ENT-06 §5 (botón "EXTRAER") | INFO | SUPUESTO |

## 5. Tributos (REG-050 a REG-059)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-050 | En cada línea gravada con IGV: `monto IGV = base × tasa`. La tasa **no es una constante**: es el parámetro `IGV` vigente en la fecha de emisión. | Anexo 9-A, págs. 9–10 (TaxableAmount, Percent, TaxAmount). Tasa: **PENDIENTE** (SUP-04) | ERROR | CITADA (estructura) / PENDIENTE (valor) |
| REG-051 | `cbc:Percent` de la línea debe ser igual a la tasa parametrizada vigente del tributo. | Anexo 9-A, pág. 10 | ERROR | CITADA / PENDIENTE (valor) |
| REG-052 | **ISC según el catálogo 08:** `01` = sistema al valor, `02` = monto fijo, `03` = precio de venta al público. Cada producto sujeto a ISC declara su sistema y sus parámetros (tasa, monto fijo o factor) en `ParametrosTributariosPort`. | Catálogo 08 (descripciones: Apéndices III y IV del TUO IGV e ISC). Las fórmulas y tasas **no** están en el workspace | ERROR | CITADA (sistemas) / **PENDIENTE** (fórmulas y tasas) |
| REG-053 | El orden de cálculo y la base del IGV cuando hay ISC (si la base del IGV incluye el ISC) deben definirse con la ley. | — | ERROR | **PENDIENTE** (TUO IGV e ISC no disponible) |
| REG-054 | **ICBPER** (tributo 7152): `monto = cantidad de bolsas (TaxSubtotal/cbc:BaseUnitMeasure, unitCode NIU) × monto unitario (TaxSubtotal/cac:TaxCategory/cbc:PerUnitAmount)`. | XSL SUNAT 06/09/2022: ValidaExprRegFactura-2.0.1, líneas 3725–3810 (errores 2892, 3237, 3238, 4318, 4320); catálogo 05 (7152). El **monto unitario vigente** sigue PENDIENTE (DISC-14) | ERROR | CITADA (estructura, validación SUNAT) / PENDIENTE (tasa) |
| REG-055 | Operaciones gratuitas (afectaciones con tributo 9996 en el catálogo 07): el precio unitario va como valor referencial con `PriceTypeCode = "02"`, y no suman al importe total. | Catálogo 16 (código 02); catálogo 07 (columna comunitaria). La exclusión del total es SUPUESTO | ERROR | SUPUESTO |
| REG-056 | En las líneas exoneradas (9997), inafectas (9998) o de exportación (9995), el monto del IGV es 0. | Catálogos 05 y 07 | ERROR | SUPUESTO |
| REG-057 | Cabecera: un `TaxSubtotal` por tributo, cuyo monto es la suma de los subtotales de las líneas con ese tributo. `TaxTotal/TaxAmount` es la suma de los subtotales de cabecera. | Anexo 9-A, pág. 7 | ERROR | CITADA (estructura) / SUPUESTO (agregación) |
| REG-058 | Un mismo tributo no aparece dos veces en la misma línea. | — | ERROR | SUPUESTO |
| REG-059 | **Los montos calculados los calcula el núcleo, no el cliente**: valor de venta, tributos (base, tasa y monto, incluidos ISC e ICBPER) y totales son `readOnly` en los contratos. El cliente envía solo los datos de origen (cantidad, valor unitario, afectación, sistema de ISC, cantidad de bolsas). Todo monto es decimal exacto (texto en JSON, `BigDecimal` en el dominio), **nunca `double` o `float`**. El correlativo también es `readOnly` (REG-035). | Diseño: evita totales manipulados y errores de redondeo binario (REG-067, REG-068) | ERROR | SUPUESTO (diseño) |

## 6. Totales y redondeo (REG-060 a REG-069)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-060 | Valor de venta de la línea = cantidad × valor unitario − descuentos de la línea que afectan la base (cat. 53 `00`) + cargos de la línea que la afectan (`47`). | Anexo 9-A, págs. 8–10; catálogo 53 | ERROR | SUPUESTO (fórmula) |
| REG-061 | Total valor de venta (`LegalMonetaryTotal/LineExtensionAmount`) = suma de los valores de venta de las líneas onerosas. | Anexo 9-A, pág. 7 | ERROR | SUPUESTO (fórmula) |
| REG-062 | Total precio de venta (`TaxInclusiveAmount`) = total valor de venta + total de tributos. | Anexo 9-A, pág. 7 ("incluye impuestos") | ERROR | SUPUESTO (fórmula) |
| REG-063 | `AllowanceTotalAmount` = suma de los descuentos globales. | Anexo 9-A, págs. 6–7 | ERROR | CITADA (definición) |
| REG-064 | `ChargeTotalAmount` = suma de los cargos globales. | Anexo 9-A, págs. 6–7 | ERROR | CITADA (definición) |
| REG-065 | `PrepaidAmount` = suma de los anticipos aplicados. | Anexo 9-A, págs. 6–7 | ERROR | CITADA (definición) |
| REG-066 | Importe total (`PayableAmount`) = precio de venta − descuentos globales + otros cargos − anticipos. | Anexo 9-A, pág. 7 | ERROR | SUPUESTO (fórmula) |
| REG-067 | Precisión: los montos tienen 2 decimales (`n(12,2)`; anticipos `n(15,2)`). Las cantidades y los valores o precios unitarios, hasta 10 decimales (`n(12,10)`). Los factores, `n(3,5)`. | Anexo 9-A, págs. 6–10 | ERROR | CITADA |
| REG-068 | El redondeo es *half-up* a 2 decimales, solo al final de cada total, y lo aplica el núcleo (REG-059). La tolerancia es un parámetro, que solo se usa para conciliar con documentos externos (CDR del OSE o sincronización offline). | — | ADVERTENCIA | PENDIENTE (regla oficial de redondeo y tolerancia) |
| REG-069 | Todo `@currencyID` del documento es igual a `DocumentCurrencyCode`. | Anexo 9-A, pág. 7 (cada monto lleva la moneda) | ERROR | SUPUESTO |

## 7. Notas de crédito y débito (REG-070 a REG-079)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-070 | Documento afectado obligatorio: serie-número (`ReferenceID` y `BillingReference/.../cbc:ID`) y tipo (catálogo 01). | Anexo 9-A, págs. 19 y 23 | ERROR | CITADA |
| REG-071 | El documento afectado existe, es del mismo emisor y está `ACEPTADO` (o es físico o de contingencia, en formato `NNNN-NNNNNNNN`). | Anexo 9-A, pág. 19 (formatos admitidos) | ERROR | SUPUESTO |
| REG-072 | El tipo del documento afectado es compatible con la serie de la nota: F → 01, B → 03. | ENT-06 §6 | ERROR | SUPUESTO |
| REG-073 | La nota conserva el adquirente y la moneda del documento afectado. La suma de NC no puede superar el importe del documento afectado. | — | ERROR | SUPUESTO |
| REG-074 | El motivo o sustento es obligatorio (`an..250`). | Anexo 9-A, págs. 19 y 23 (0..n en el anexo) | ERROR | SUPUESTO (obligatoriedad) |

## 8. Fechas y horas (REG-080 a REG-089)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-080 | La fecha de emisión tiene el formato `yyyy-mm-dd` y no es futura. | Anexo 9-A, pág. 1; manual Nubefact ("Debe ser la fecha actual") | ERROR | CITADA (formato) / SUPUESTO (no futura) |
| REG-081 | Fecha de vencimiento ≥ fecha de emisión. | Manual Nubefact ("fecha posterior a la fecha de emisión") | ERROR | SUPUESTO (fuente de mercado) |
| REG-082 | La hora de emisión tiene el formato `hh:mm:ss` (`xsd:time`). | XSD `udt:TimeType`; DISC-16 (el anexo dice `hh-mm-ss.0z`) | ERROR | CITADA (XSD) |

## 9. Firma digital (REG-090 a REG-099)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-090 | Todo documento enviado lleva `ds:Signature` en `ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent`. | Anexo 9-A, págs. 1, 19, 23, 28 y 31 | ERROR | CITADA |
| REG-091 | El certificado es vigente a la fecha de firma y pertenece al RUC emisor. | RS 097-2012 (requisito de certificado: **no** está en el workspace) | ERROR | PENDIENTE |
| REG-092 | `cac:Signature` identifica al firmante (RUC emisor) y referencia la firma (`#ID`). | Anexo 9-A, pág. 3 | ERROR | CITADA (existencia) / SUPUESTO (contenido) |
| REG-094 | **El XML UBL se valida contra el XSD ANTES de firmar** (`ValidadorXsdPort`). Si no valida, no se firma, no se envía, el comprobante no pasa a `EMITIDO` y el correlativo reservado se libera dentro de la misma transacción. Validar después de firmar está prohibido: si la firma se aplica a un XML inválido, se desperdicia la firma y se rompe la atomicidad. El XML se genera con clases derivadas del XSD (ADR-007), así que el XSD actúa como red de seguridad y no como la única barrera. | `mapa-xsd.md` §2–§3 (el XSD valida estructura; la firma va en `ExtensionContent`); ADR-007 | ERROR | SUPUESTO (diseño) |
| REG-093 | La clave privada nunca sale del almacén seguro (Windows CNG/DPAPI, Android Keystore) y nunca se serializa en DTOs, logs ni archivos. | RNF-07; ADR-004 y ADR-006 | ERROR | SUPUESTO (seguridad) |

## 10. Longitudes y texto (REG-100)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-100 | Cada campo de texto respeta la longitud máxima del anexo (columna `tipo_longitud` de la matriz). Por ejemplo, razón social `an..100`, descripción `an..250`, orden de compra `an..20`, código de producto `an..30`. | Anexo 9-A (por fila) | ERROR | CITADA |

## 11. Plazos (REG-110 a REG-119)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-110 | Plazo máximo para enviar un comprobante al OSE o a SUNAT desde su emisión (incluido el modo sin conexión). | Manual Nubefact, error 22 "fuera del plazo permitido" (existe un plazo, pero su valor no figura) | ERROR | **PENDIENTE** |
| REG-111 | Plazos de la comunicación de baja y del resumen diario respecto de la fecha de referencia. | — | ERROR | **PENDIENTE** |

## 12. Resumen diario y comunicación de baja (REG-120 a REG-129)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-120 | Identificador del resumen: `RC-<Fecha>-#####` (`an..17`). Cada línea lleva serie-número (`an..13`). | Anexo 9-A, pág. 28 | ERROR | CITADA |
| REG-121 | Identificador de la baja: `RA-<Fecha>-#####` (`an..17`). Los números de línea (`LineID`) son consecutivos (`n..5`). | Anexo 9-A, págs. 28 y 31 | ERROR | CITADA |
| REG-122 | `IssueDate` es la fecha de generación y `ReferenceDate` la fecha de emisión de los documentos incluidos. Todos los documentos de un envío comparten `ReferenceDate`. | Anexo 9-A, págs. 28 y 31. La fecha compartida es SUPUESTO | ERROR | CITADA / SUPUESTO |
| REG-123 | El estado de cada ítem del resumen pertenece al catálogo 19. | Anexo 9-A, pág. 29 | ERROR | PENDIENTE (catálogo 19 no disponible) |
| REG-124 | Baja: serie `an4`, correlativo `n..8`, motivo `an..100`. Solo se da de baja un documento previamente `ACEPTADO`. Resumen: los totales por tipo usan el catálogo 11 (DISC-09). | Anexo 9-A, págs. 29 y 31. Lo de "previamente aceptado" es SUPUESTO | ERROR | CITADA / SUPUESTO |

## 13. Migración del legado (REG-130 a REG-139)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-130 | Una ficha con fecha inválida o vacía va a **cuarentena**; no se migra con una fecha inventada. | R-01; ADR-005 | ERROR (por ficha) | SUPUESTO |
| REG-131 | Una ficha con `ingreso` y `salida` informados a la vez se divide en dos movimientos que conservan el mismo origen, o va a cuarentena si la política lo indica. | R-01; ADR-005 | ADVERTENCIA | SUPUESTO |
| REG-132 | Un producto sin código recibe un **código provisional** (`LEG-<hash>`), marcado `requiereHomologacion = true`. | R-01; brecha del formato 12.1 (código de existencia) | ADVERTENCIA | SUPUESTO |
| REG-133 | Un `nro_documento` repetido no se fusiona: se conservan todas las fichas, cada una con su `origen.fila`, y se reporta. | R-01 | ADVERTENCIA | SUPUESTO |
| REG-134 | Toda entidad migrada conserva `origen = {fuente: LEGADO, archivo, fila, hashFila, loteImportacion}` y es inmutable. | R-01; RNF-05 | ERROR | SUPUESTO |
| REG-135 | La cantidad de un movimiento es > 0. El saldo resultante no puede ser negativo sin generar una advertencia. | — | ADVERTENCIA | SUPUESTO |

## 14. Registros 14.1, 8.1 y 12.1 (REG-140 a REG-149)

> **Fuente nueva (27/10):** los Excel de `Git/`, extraídos a [`referencias/formatos/`](../../referencias/formatos/) por `tools/extraer_formatos_excel.py`. Son **plantillas comunitarias**: la estructura PLE (hoja "Estructura" del `.xlsm`, que cita la RS 286-2009-SUNAT) y los formatos impresos 14.1, 8.1 y 13.1. Se usan como fuente citada, pero deben contrastarse con la publicación oficial vigente de SUNAT.

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-140 | El registro de ventas 14.1 se genera por período a partir de los comprobantes del período, con los campos 1 a 35 de la estructura PLE (`registro-ventas-14-1.schema.yaml`, `x-campo-ple`). La versión impresa (22 columnas) es un subconjunto. | Estructura PLE 14.1 (`referencias/formatos/estructura-ple-14-1.csv`); formato impreso `Git/234_formato141.pdf` (RS 234-2006), que coincide con `Git/registro ventas formato 14.1.xls` | ERROR | CITADA (PDF del formato + estructura PLE comunitaria) |
| REG-141 | El registro de compras 8.1 se genera por período a partir de los comprobantes **recibidos** de proveedores, con los campos 1 a 42 de la estructura PLE. | Estructura PLE 8.1 (`estructura-ple-8-1.csv`); plantilla simplificada `Git/592044723-FORMATO-8-1.xlsx` (DISC-19) | ERROR | CITADA (fuente comunitaria) |
| REG-142 | El registro 12.1 se genera por período, establecimiento y existencia, a partir de los movimientos de almacén. Cabecera: denominación, período, RUC y razón social, establecimiento, código de la existencia (Tabla 5), descripción y unidad (Tabla 6). Detalle mínimo: fecha, tipo (Tabla 10), serie y número del documento de traslado, comprobante o documento interno, tipo de operación (Tabla 12), entradas, salidas, saldo final en unidades y totales. | `Git/FORMATO_12_1.pdf` (ítems a–g de cabecera y a–i de detalle) | ERROR | CITADA (formato) / **PENDIENTE** (tablas 5, 6 y 12) |
| REG-148 | En el 12.1, el **saldo inicial** se consigna en la columna de **entradas** (primera fila del período), y cada existencia cierra con **totales**: Σ entradas, Σ salidas y saldo final = saldo inicial + entradas − salidas. | `Git/FORMATO_12_1.pdf`, ítems f, h e i. La fórmula del saldo es SUPUESTO aritmético | ERROR | CITADA / SUPUESTO (fórmula) |
| REG-143 | Formato del archivo PLE: período `AAAAMM00` con 01 ≤ MM ≤ 12; fechas `DD/MM/AAAA`; montos de hasta 12 enteros y 2 decimales, **sin comas de miles** (aceptan negativos). El contrato JSON usa fechas ISO y la conversión la hace `GeneradorRegistrosPort`. | Estructura PLE 14.1 y 8.1 (campos 1, 4 y 13 a 25) | ERROR | CITADA (fuente comunitaria) |
| REG-144 | Si el tipo es 07, 08, 87 u 88, son obligatorios la fecha, el tipo, la serie y el número del comprobante modificado (14.1: campos 28 a 31; 8.1: campos 27 a 29 y 31). | Estructura PLE 14.1 (campos 28–31), 8.1 (campos 27–31) | ERROR | CITADA (fuente comunitaria) |
| REG-145 | Si se informa la moneda, el tipo de cambio es obligatorio, con formato `#.###` y positivo. | Estructura PLE 14.1 (campo 27), 8.1 (campo 26) | ERROR | CITADA (fuente comunitaria) |
| REG-146 | Estado de la anotación: 14.1 campo 35 ∈ {0, 1, 2, 8, 9}; 8.1 campo 42 ∈ {0, 1, 6, 7, 9}. Ejemplos: 1 = la operación corresponde al período; 2 = documento inutilizado; 8 = anotación omitida de un período anterior. | Estructura PLE (RS 286-2009-SUNAT, art. 8 inc. e, citada en la plantilla) | ERROR | CITADA (fuente comunitaria) |
| REG-147 | El tipo de comprobante del registro usa la **Tabla 10** PLE. Para 01, 03, 07 y 08 coincide con el catálogo 01, así que el registro se puede proyectar sin mapear. La moneda usa la **Tabla 4** y el documento de identidad, la **Tabla 2** (DISC-21). | `referencias/formatos/tablas-ple.json` | ADVERTENCIA | CITADA (fuente comunitaria) |

## 15. Integración, idempotencia y modo sin conexión (REG-150 a REG-179)

| ID | Regla | Fuente | Severidad | Estado |
|---|---|---|---|---|
| REG-150 | El dominio usa solo los códigos SUNAT. Los códigos propietarios (por ejemplo, Nubefact `tipo_de_comprobante` 1–4, `sunat_transaction`, `tipo_de_igv` o `moneda` 1–4) existen solo en el adaptador de salida. | RNF-09; DISC-15 | ERROR | SUPUESTO (arquitectura) |
| REG-160 | Toda operación que crea algo acepta `Idempotency-Key`. Un reintento con la misma clave y el mismo cuerpo devuelve el mismo resultado sin consumir un nuevo correlativo. La misma clave con otro cuerpo devuelve 409. | RNF-04; manual Nubefact (`codigo_unico`) | ERROR | SUPUESTO |
| REG-170 | Sin conexión, el dispositivo emite con las series de contingencia **asignadas a ese dispositivo** y encola el envío. Cada envío se reintenta con *backoff* hasta su aceptación o rechazo definitivo. | ADR-006; ENT-06 §6. Las condiciones normativas de la contingencia son PENDIENTE | ERROR | SUPUESTO / PENDIENTE |
