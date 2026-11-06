# Formatos de libros: referencias extraídas de los Excel de `Git/`

> **GENERADO** por `tools/extraer_formatos_excel.py` (salvo este README). Los Excel originales quedan **intactos** en `Git/`.
> ⚠ **Fuente comunitaria, no oficial.** Son plantillas descargadas de internet. La hoja "Estructura" del `.xlsm` transcribe la estructura del PLE y cita la RS 286-2009-SUNAT, pero **debe contrastarse con la publicación oficial vigente de SUNAT** antes de usarse en producción.
> **Seguridad:** del `.xlsm` solo se leyeron las hojas `Estructura`, `Reglas` y `Tablas Generales`. **No** se abrieron `Pasword`, `Inicio` ni `Sistema`, y las macros no se ejecutaron. Tampoco se copiaron las filas de datos de ejemplo, porque contienen RUC y razones sociales de terceros.

## Archivos de origen

| Archivo en `Git/` | Contenido real | Uso |
|---|---|---|
| `234_formato141.pdf` (28/10) | Formato **impreso** 14.1 de la RS 234-2006 (2 páginas, 22 columnas) | Fuente de REG-140. Coincide columna por columna con el `.xls` siguiente |
| `FORMATO_12_1.pdf` (28/10) | Texto del **Formato 12.1**: cabecera (ítems a–g) e información mínima (ítems a–i). El documento no indica su procedencia | Fuente de REG-142 y REG-148. Los ítems se transcriben en `tools/construir_matriz.py` (`ITEMS_121`) |
| `registro ventas formato 14.1.xls` | Formato **impreso** 14.1 (22 columnas; no trae ICBPER ni IVAP) | `plantillas-columnas.json` → `14.1` |
| `592044723-FORMATO-8-1.xlsx` | Formato 8.1 **simplificado** (19 columnas, con columnas contables "DIVISIONARIA") | `plantillas-columnas.json` → `8.1` (DISC-19) |
| `464918148-11-FORMATO-DE-KARDEX-SEGUN-SUNAT-xls.xls` | **Formato 13.1**, inventario permanente **valorizado** (el 12.1 viene en el PDF) | `plantillas-columnas.json` → `13.1`, solo como referencia (DISC-18 cerrada, DISC-23) |
| `Macro excel Registro de compras y ventas excel 2019 MOD.xlsm` | Estructura PLE 8.1, 8.2, 8.3, 14.1 y 14.2; regla general por Tabla 10; tablas PLE | `estructura-ple*.{json,csv}`, `reglas-generales-tabla10.csv`, `tablas-ple.json` |
| `Macro excel ... MOD (1).xlsm` | **Duplicado exacto** del anterior (mismo SHA-256) | No se usa |
| `registro ventas excel.xlsm` | Plan contable, Tabla 10 y un registro de ejemplo con RUC de terceros | No se extrae (no aporta estructura nueva) |

## Archivos generados

| Archivo | Qué contiene |
|---|---|
| `plantillas-columnas.json` | Cabecera y columnas (encabezados unidos) de los formatos impresos 14.1, 8.1 y 13.1 |
| `estructura-ple.json` | Campos de los libros 8.1 (42 + libres), 8.2, 8.3, 14.1 (35 + libres) y 14.2, con longitud, obligatoriedad, llave, formato, observaciones y notas al pie |
| `estructura-ple-8-1.csv`, `-8-2`, `-8-3`, `-14-1`, `-14-2` | Lo mismo, en CSV para Excel |
| `tablas-ple.json` | Tablas PLE 1, 2, 3, 4, 10, 11, 25, 27, 30, 31, 32, 33 y 35. Se omite la 17 (plan de cuentas). **No** están las tablas 5, 6 ni 12 que exigen los formatos 12.1 y 13.1 |
| `reglas-generales-tabla10.csv` | Regla general por tipo de comprobante (Tabla 10): si aplica al 14.1, 14.2, 8.1, etc., y la longitud y validación de la serie y el número |

## Qué se incorporó a los specs

- `registro-ventas-14-1.schema.yaml` y `registro-compras-8-1.schema.yaml`: un campo por cada campo PLE (`x-campo-ple`).
- Reglas REG-140, REG-141 y REG-143 a REG-147. REG-045 ahora tiene una fuente parcial (umbral de 700.00 en la boleta).
- `registro-inventario-12-1.schema.yaml`: un campo por cada ítem del PDF (`x-item-121`), y las reglas REG-142 y REG-148.
- Discrepancias DISC-18 a DISC-23. DISC-14 quedó actualizada: el ICBPER aparece en el campo 23 del PLE 14.1.
- [`../../specs/05-trazabilidad/matriz-registros-ple.md`](../../specs/05-trazabilidad/matriz-registros-ple.md): campo PLE o ítem del 12.1 ↔ propiedad del schema ↔ fila MT del Anexo 9-A.
