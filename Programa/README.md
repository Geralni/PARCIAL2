# ABC Software Corp: Facturación electrónica SUNAT (Fase 1, SPEC-FIRST)

> **Examen de medio curso de Arquitectura de Software (UNAS, FIIS).**
> **Fase 1** = esqueleto de especificaciones técnicas: reglas, contratos de datos, validaciones y contratos de interfaz. **No hay lógica de negocio implementada.**
> **Fuentes:** solo la carpeta `Git/` (de solo lectura, sin modificar): el Anexo 9-A (RS 117-2017), los catálogos del Anexo 8 (fuente **comunitaria no oficial**, 2020), el XSD **OASIS UBL 2.1** (`Git/UBL-2.1/xsd`, con control cruzado en 2.2), las **hojas XSL de validación de SUNAT** (06/09/2022; prevalecen sobre el anexo de 2017), el manual de la API de Nubefact y las observaciones del DEMO.
> **Convención:** toda regla cita su fuente. Lo que no tiene fuente se marca `SUPUESTO` o `PENDIENTE` y aparece en las preguntas abiertas.

## Los 4 entregables

| # | Entregable | Dónde | Empiece por |
|---|---|---|---|
| 1 | **Modelo de dominio y contratos (DTOs/Schemas)** | [`specs/02-dominio-y-contratos/`](specs/02-dominio-y-contratos/) | [modelo-dominio.md](specs/02-dominio-y-contratos/modelo-dominio.md) → [schemas/](specs/02-dominio-y-contratos/schemas/) (27 schemas en **YAML**, formato JSON Schema 2020-12) → [reglas-de-validacion.md](specs/02-dominio-y-contratos/reglas-de-validacion.md) (104 reglas) → [dtos/](specs/02-dominio-y-contratos/dtos/) (Kotlin) |
| 2 | **Arquitectura MVC con visión hexagonal** | [`specs/03-arquitectura/`](specs/03-arquitectura/) | [mvc-hexagonal.md](specs/03-arquitectura/mvc-hexagonal.md) (6 diagramas, incluida la ruta de transición MVC → Hexagonal) → [adr/](specs/03-arquitectura/adr/) (ADR-001 a ADR-007) |
| 3 | **Especificación de endpoints y servicios (contratos API)** | [`specs/04-api/`](specs/04-api/) | [puertos.md](specs/04-api/puertos.md) (el contrato real) → [openapi.yaml](specs/04-api/openapi.yaml) (OpenAPI 3.1, 24 operaciones) |
| 4 | **Matriz de trazabilidad normativa** | [`specs/05-trazabilidad/`](specs/05-trazabilidad/) | [matriz-trazabilidad.md](specs/05-trazabilidad/matriz-trazabilidad.md) (173 filas, Anexo 9-A + validación SUNAT ↔ UBL, con códigos de error SUNAT) · [CSV](specs/05-trazabilidad/matriz-trazabilidad.csv) · [matriz-registros-ple.md](specs/05-trazabilidad/matriz-registros-ple.md) (93 campos e ítems: PLE 14.1/8.1 y 12.1 ↔ schema ↔ MT) · [discrepancias.csv](specs/05-trazabilidad/discrepancias.csv) (25; 12 cerradas) |

## 2.º parcial: generador de XML UBL 2.1 (implementación)

La carpeta [`generador-ubl/`](generador-ubl/) contiene la **implementación en Kotlin** de la generación del XML a partir de `UBL-Invoice-2.1.xsd`, con **46 pruebas unitarias**. Se ejecuta con `mvn test` desde esa carpeta (requiere JDK 21+ y Maven). Las clases se generan desde el XSD (ADR-007), se valida contra el XSD antes de devolver el XML (REG-094) y se usan los nombres del modelo de dominio. Detalle en [`generador-ubl/README.md`](generador-ubl/README.md).

## Cómo leerlo (orden sugerido)

1. [`specs/00-analisis-del-caso.md`](specs/00-analisis-del-caso.md): requisitos, restricciones, supuestos, riesgos y preguntas abiertas.
2. [`specs/01-casos-de-uso.md`](specs/01-casos-de-uso.md): 13 casos de uso contrastados con Nubefact DEMO, cada uno con su puerto y sus operaciones.
3. [`specs/02-dominio-y-contratos/catalogs/INDEX.md`](specs/02-dominio-y-contratos/catalogs/INDEX.md) y [`mapa-xsd.md`](specs/02-dominio-y-contratos/mapa-xsd.md): qué dice la norma y qué valida (y qué no) el XSD.
4. Entregables 1 → 2 → 3 → 4.
5. [`specs/06-migracion/mapeo-legado.md`](specs/06-migracion/mapeo-legado.md): de la ficha del legado al nuevo dominio sin perder trazabilidad.

**Cadena de trazabilidad:** dato SUNAT (Anexo 9-A, página) → `MT-xxx` (matriz) → XPath verificado en el XSD → `REG-xxx` (regla) → propiedad del schema (`x-trazabilidad`) → campo del DTO (`// MT-xxx`) → `operationId` → puerto de entrada → `CU-xx` → origen en el legado.

## Estructura

```
Programa/
  README.md
  referencias/sunat-xsl/     reglas de la validación SUNAT vigente (3 378 reglas, 891 códigos de error)
  referencias/formatos/      estructura PLE 8.1/8.2/8.3/14.1/14.2, tablas PLE y columnas de los formatos
                             impresos 14.1, 8.1 y 13.1, extraídas de los Excel de Git/ (fuente comunitaria)
  specs/
    00-analisis-del-caso.md, 01-casos-de-uso.md
    02-dominio-y-contratos/  modelo-dominio.md, mapa-xsd.md, reglas-de-validacion.md,
                             schemas/*.schema.yaml, dtos/**/*.kt, catalogs/cat*.json + INDEX.md
    03-arquitectura/         mvc-hexagonal.md, adr/ADR-001..007
    04-api/                  openapi.yaml, puertos.md
    05-trazabilidad/         matriz-trazabilidad.csv/.md, discrepancias.csv
    06-migracion/            mapeo-legado.md
  samples/                   JSON y XML UBL de ejemplo; legado/fichas-ejemplo.csv (FICTICIO)
  tools/                     scripts de verificación (Python 3)
  generador-ubl/             2.º parcial: generador Kotlin de XML UBL 2.1 Invoice + pruebas unitarias (mvn test)
```

## Datos ficticios

Todo lo que hay en [`samples/`](samples/) es **ficticio**: RUC, DNI, nombres, montos y las **30 fichas del legado** (`samples/legado/fichas-ejemplo.csv`, con casos sucios a propósito). Las tasas de los ejemplos (IGV 18.00 tomado del DEMO, ISC 10.00 inventado) son **ilustrativas y no están verificadas**. En los contratos, las tasas son **parámetros con vigencia** (`parametro-tributario.schema.yaml`). Ver [samples/README.md](samples/README.md).

## Seguridad

Ningún archivo contiene tokens, rutas de API reales ni certificados. Las credenciales de proveedores se nombran `<RUTA>` y `<TOKEN>`. `tools/validar_contratos.py` (V6) busca patrones de credenciales.

## Verificación (PASO 9)

```powershell
# Desde "C:\proyects-curso\ABC Software Corp\Programa"
pip install -r tools\requirements.txt     # una vez (jsonschema, pyyaml, lxml, openapi-spec-validator, openpyxl, xlrd)
python tools\convertir_catalogos.py       # regenera catalogs/*.json y schemas/catalogos.schema.yaml desde Git/
python tools\extraer_formatos_excel.py    # regenera referencias/formatos/ desde los Excel de Git/ (sin ejecutar macros)
python tools\extraer_reglas_xsl.py       # regenera referencias/sunat-xsl/reglas-xsl.csv desde las XSL de SUNAT
python tools\construir_matriz.py          # regenera las matrices (Anexo 9-A y registros PLE) y discrepancias; verifica XPath
python tools\verificar_matriz.py          # M1-M11: XPath en el XSD UBL 2.1 (y control 2.2), trazabilidad en ambos sentidos, CU ↔ API ↔ puertos, PLE/12.1 ↔ schema
python tools\validar_contratos.py         # V1-V6: meta-schema, catálogos, OpenAPI 3.1, samples JSON/XML, credenciales
python tools\generar_mapa_xsd.py          # (opcional) regenera las tablas de mapa-xsd.md §5
```

Último resultado: **todo OK**. Matriz con 173 filas: 136 XPath verificados en el XSD UBL 2.1 (0 diferencias con 2.2), 30 verificados en la validación SUNAT (XSL) y solo 7 PENDIENTE. 93 campos e ítems de registros cubiertos. 27 schemas válidos. OpenAPI 3.1 válido y sin advertencias en Redocly (`recommended` y `recommended-strict`). 7 JSON y 2 XML de ejemplo válidos.

## Exportación a PDF e imágenes

No se exportó, porque `mermaid-cli` y `pandoc` no están instalados en el equipo. Los diagramas se ven en VS Code (extensión *Markdown Preview Mermaid Support*) o en GitHub. Para exportar:

```powershell
npm install -g @mermaid-js/mermaid-cli     # mmdc: diagramas -> PNG/SVG (descarga Chromium)
winget install --id JohnMacFarlane.Pandoc  # pandoc: .md -> .docx/.pdf (para PDF hace falta además un motor LaTeX, p. ej. MiKTeX)
```

## Pendientes principales

- **Anexos posteriores a 2019** (RS 114-2019, 150-2019 y 193-2020): ICBPER, forma de pago con cuotas y validaciones vigentes.
- XSD SUNAT de `SummaryDocuments` y `VoidedDocuments`: solo quedan 7 filas PENDIENTE (las XSL de SUNAT ya confirman las demás).
- **Tablas 5, 6 y 12** (existencia, unidad de medida y tipo de operación) del 12.1. Mientras falten, el tipo de operación se registra como `PENDIENTE` y no se exporta el registro oficial. Además, hay que contrastar con la fuente oficial la estructura PLE del 14.1 y el 8.1, que es comunitaria.
- **Anexo 8 oficial** y catálogos 11, 12 y 19; tasas vigentes; algoritmo del dígito verificador del RUC; norma de contingencia.
- **Contraste con Nubefact:** falta emitir un comprobante de prueba y revisar las reseñas de usuarios.
