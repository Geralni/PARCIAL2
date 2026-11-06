# Ejemplos (samples)

> ⚠ **TODOS LOS DATOS SON FICTICIOS.** Los RUC (`20000000001`, `20000000002`) y el DNI (`00000001`) son inventados y no se verificó su dígito verificador. Los nombres, productos y montos son ilustrativos.
> ⚠ **Tasas ilustrativas, no verificadas:** el IGV de 18.00 se tomó del DEMO de Nubefact (ENT-06), que **no** es una fuente normativa (SUP-04). El ISC de 10.00 (sistema al valor) es **inventado** solo para mostrar el catálogo 08 (REG-052 PENDIENTE). En la línea con ISC, la base del IGV incluye el ISC según un SUPUESTO pendiente de ley (REG-053).
> **Campos `readOnly`:** los JSON de comprobante y nota muestran la **representación completa** que devuelve el sistema, incluidos los montos calculados (`valorVenta`, `tributos`, `totales`). En una **petición**, el cliente no los envía: los calcula el núcleo (REG-059).
> ⚠ **Firma:** el `ds:Signature` de los XML es un **marcador estructural**: no es criptográficamente válido.

| Archivo | Qué muestra | Valida contra |
|---|---|---|
| `factura-01.json` | Factura F001 con 2 líneas (una con ISC del catálogo 08) y crédito en 2 cuotas | `comprobante.schema.yaml` |
| `boleta-03.json` | Boleta B001 con DNI y una línea con ICBPER (PENDIENTE) | `comprobante.schema.yaml` |
| `nota-credito-07.json` | NC por devolución por ítem (catálogo 09, código 07) que modifica F001-1 | `nota.schema.yaml` |
| `comunicacion-baja.json` | Baja de F001-2 | `comunicacion-baja.schema.yaml` |
| `resumen-diario.json` | Resumen con una boleta | `resumen-diario.schema.yaml` |
| `registro-ventas-14-1.json` | Registro 14.1 de octubre de 2026 con la factura y la NC de ejemplo (campos PLE) | `registro-ventas-14-1.schema.yaml` |
| `registro-inventario-12-1.json` | Registro 12.1 de enero de 2024 de ARR-050, construido con las fichas 1, 2 y 8 del legado ficticio. El tipo de operación es `PENDIENTE` porque falta la Tabla 12 | `registro-inventario-12-1.schema.yaml` |
| `xml/F001-1.xml` | La misma factura en UBL con la estructura vigente de SUNAT: emisor y adquirente en `PartyIdentification`/`PartyLegalEntity`, tipo de operación en `InvoiceTypeCode/@listID` y firma en `ExtensionContent` | XSD UBL 2.1 `Invoice` (y 2.2) |
| `xml/F001-NC-1.xml` | La misma NC en UBL | XSD UBL 2.1 `CreditNote` (y 2.2) |
| `legado/fichas-ejemplo.csv` | **30 fichas FICTICIAS** del legado con casos sucios: producto sin código, documento repetido, fecha inválida, ingreso y salida a la vez, cantidad no numérica o negativa | `ficha-legado.schema.yaml` (clasificación esperada en `specs/06-migracion/mapeo-legado.md §4`) |

Se validan con `python tools/validar_contratos.py` (V4 y V5). El XSD **no** valida las reglas SUNAT (mapa-xsd.md §3): que un XML valide no significa que SUNAT lo acepte.
