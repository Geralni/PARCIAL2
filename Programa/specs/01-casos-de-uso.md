# 01 — Casos de uso

> **Base:** [`Git/observaciones-nubefact-demo.md`](../../Git/observaciones-nubefact-demo.md) (ENT-06), el manual de la API de Nubefact (ENT-05) y los requisitos de [00-analisis-del-caso.md](00-analisis-del-caso.md).
> ⚠ **Contraste con Nubefact DEMO:** son observaciones del estudiante. **Falta emitir un comprobante de prueba y revisar las reseñas de usuarios.** Tampoco se capturaron el formulario de línea (unidad, afectación, ISC), un comprobante emitido (estados y descargas), los resúmenes de boletas ni la nota de débito (ENT-06 §11).
> Cada caso de uso tiene un **puerto de entrada** ([puertos.md](04-api/puertos.md)) y al menos una **operación OpenAPI** ([openapi.yaml](04-api/openapi.yaml)). `tools/verificar_matriz.py` (M9) lo comprueba.

## Actores

| Actor | Descripción | Plataforma |
|---|---|---|
| Vendedor o cajero | Emite boletas y facturas en tienda o en ruta | Android (APK), Windows |
| Administrador | Configura locales, series y productos; emite notas y bajas | Windows (MSI) |
| Contador | Resúmenes, registros 14.1, 8.1 y 12.1, conciliación | Windows |
| Sistema (planificador) | Reintentos, resumen diario automático y consulta de tickets | Nodo Windows |
| OSE / SUNAT | Valida y devuelve el CDR o un ticket | Externo |

## Resumen de trazabilidad

| CU | Nombre | Puerto de entrada | Operaciones OpenAPI | Contraste con Nubefact |
|---|---|---|---|---|
| CU-01 | Emitir factura o boleta | `EmitirComprobanteUseCase` | `emitirComprobante` | «Emitir comprobante electrónico» y «Generar comprobante» (§2); API operación 1 |
| CU-02 | Consultar comprobante y descargar XML/CDR | `ConsultarComprobanteUseCase` | `buscarComprobantes`, `consultarComprobante`, `descargarXml`, `descargarCdr` | «Consolidado» (§7); API operación 2 |
| CU-03 | Emitir nota de crédito | `EmitirNotaUseCase` | `emitirNotaCredito` | Selector «Nota de crédito» (§2) |
| CU-04 | Emitir nota de débito | `EmitirNotaUseCase` | `emitirNotaDebito` | No se capturó (§11) |
| CU-05 | Comunicar baja (2 pasos) | `ComunicarBajaUseCase` | `crearComunicacionBaja`, `consultarEstadoBaja` | «Comunicaciones de baja» (§8); API operaciones 3 y 4 |
| CU-06 | Enviar resumen diario | `EnviarResumenDiarioUseCase` | `crearResumenDiario`, `consultarEstadoResumen` | Módulo «Resúmenes de Boletas» (no se capturó) |
| CU-07 | Gestionar series y correlativos | `GestionarSeriesUseCase` | `listarSeries`, `crearSerie`, `asignarSeriesContingencia` | «Locales y Series» (§6) |
| CU-08 | Consultar catálogos | `ConsultarCatalogoUseCase` | `listarCatalogos`, `obtenerCatalogo` | Las listas de la UI (IGV, tipo de operación) |
| CU-09 | Validar RUC o documento | `ValidarDocumentoIdentidadUseCase` | `validarRuc` | Botón «EXTRAER» en Entidades (§5) |
| CU-10 | Importar el legado | `ImportarLegadoUseCase` | `importarLegado`, `consultarImportacion` | Sin equivalente (es propio de ABC) |
| CU-11 | Generar registros 14.1, 8.1 y 12.1 | `GenerarRegistroUseCase` | `generarRegistro` | «Descarga Excel» y Reportes (§7) |
| CU-12 | Reintentar envío y sincronizar el dispositivo | `ReintentarEnvioUseCase`, `SincronizarDispositivoUseCase` | `reenviarComprobante`, `sincronizarLoteOffline` | Columna «Offline», series de contingencia (§6) y `generado_por_contingencia` (API) |
| CU-13 | Gestionar productos | `GestionarProductosUseCase` | `listarProductos`, `registrarProducto` | «Catálogo de productos» (§4) |

---

## CU-01 Emitir factura o boleta

- **Actor:** vendedor o cajero. **Disparador:** una venta.
- **Precondiciones:** emisor configurado; establecimiento con código SUNAT; serie activa del tipo (REG-037); parámetros tributarios vigentes **verificados** (RNF-06); catálogos cargados.
- **Flujo principal:**
  1. El vendedor elige el tipo (01 o 03), la serie, el cliente, la moneda y el tipo de operación (catálogo 51, por defecto 0101).
  2. Agrega líneas: producto, cantidad, unidad (cat. 03), valor unitario, afectación del IGV (cat. 07) y, si corresponde, el ISC con su sistema (cat. 08) y el ICBPER.
  3. Elige la forma de pago (contado o crédito con cuotas, ENT-06 §3).
  4. El sistema valida las reglas (REG-003 a REG-069 y REG-080 a REG-082) y recalcula los tributos y totales.
  5. Reserva el correlativo de forma atómica (REG-034, REG-035) y genera el UBL con las clases derivadas del XSD (ADR-007).
  6. **Valida el XML contra el XSD antes de firmar** (REG-094). Si falla, se revierte la transacción: no se firma ni se consume el correlativo, y se devuelve 422.
  7. Firma el XML (REG-090).
  8. Guarda el comprobante como `EMITIDO`, lo encola para el OSE y devuelve la representación.
  9. El OSE responde con el CDR → `ACEPTADO`, `OBSERVADO` o `RECHAZADO`.
- **Flujos alternos:**
  - **A1. Borrador:** «Guardar como borrador» (ENT-06 §2) → `BORRADOR`, sin correlativo.
  - **A2. Sin conexión (Android):** se usa una serie de contingencia del dispositivo y se encola (ADR-006, CU-12).
  - **A3. OSE caído:** el comprobante queda `EMITIDO` y encolado (`PROVEEDOR_NO_DISPONIBLE` no es un error para el usuario).
  - **A4. Regla incumplida:** 422 con `violaciones[REG-xxx]` y el campo; no se consume el correlativo.
  - **A5. Reintento del cliente:** la misma `Idempotency-Key` devuelve el mismo comprobante (REG-160).
  - **A6. Boleta con cliente «VARIOS»:** permitida bajo el umbral (REG-045, PENDIENTE).
- **Reglas:** REG-003 a REG-069, REG-080 a REG-082, REG-090, REG-094, REG-150 y REG-160. El cliente **no** envía montos calculados ni el correlativo (REG-059).
- **Endpoint:** `POST /comprobantes` (`emitirComprobante`).
- **Contraste con Nubefact:** la pantalla única coincide (cliente, serie, número referencial, IGV %, tipo de operación, moneda, vencimiento, «¿Pagado?»). Diferencias: (1) Nubefact usa códigos propios (`tipo_de_comprobante` 1–4, `sunat_transaction`, `tipo_de_igv`), mientras que aquí se usan los **catálogos SUNAT** y el mapeo va en el adaptador. (2) El panel de totales de Nubefact **no muestra el ISC** (ENT-06 §2); aquí el ISC con su sistema de cálculo es explícito por línea. (3) Nubefact pide la fecha en `DD-MM-AAAA` (manual); aquí es `yyyy-mm-dd`.

## CU-02 Consultar comprobante y descargar XML/CDR

- **Actor:** administrador o contador. **Precondición:** el comprobante existe.
- **Flujo:** se filtra por fechas, tipo, serie, establecimiento o estado → se abre el detalle → se descarga el XML firmado o el CDR.
- **Alternos:** sin CDR todavía → 409 (estado `EMITIDO` o `ENVIADO`). No existe → 404.
- **Reglas:** RNF-08 (el XML y el CDR son inmutables).
- **Endpoints:** `GET /comprobantes`, `GET /comprobantes/{id}`, `GET /comprobantes/{id}/xml`, `GET /comprobantes/{id}/cdr`.
- **Contraste con Nubefact:** el «Consolidado» muestra **todos los locales** (ENT-06 §7). Se replica con el filtro opcional `establecimiento`. No se vieron estados ni descargas porque la lista estaba vacía.

## CU-03 Emitir nota de crédito

- **Actor:** administrador. **Precondiciones:** el documento afectado existe, es del mismo emisor y está `ACEPTADO` (REG-071).
- **Flujo:** se indica el documento afectado (tipo, serie y número) → se elige el motivo (catálogo 09) y se escribe el sustento → se ajustan las líneas → se valida y emite igual que en CU-01.
- **Alternos:** el afectado no existe → 404. La serie no coincide (F/B) → 422 (REG-032). El monto supera el saldo → 422 (REG-073). Con el motivo 01 (anulación), el afectado pasa a `ANULADO` cuando la NC es aceptada.
- **Reglas:** REG-007, REG-018, REG-032 y REG-070 a REG-074.
- **Endpoint:** `POST /notas-credito`.
- **Contraste con Nubefact:** al elegir NC aparecen «Documento a modificar», «Serie», «Número» y «Tipo Nota de Crédito», y desaparece la detracción (ENT-06 §2). Nubefact codifica el tipo de NC con enteros propios; aquí se usa el catálogo 09.

## CU-04 Emitir nota de débito

- **Actor:** administrador. **Precondición:** igual que en CU-03.
- **Flujo:** igual que en CU-03, con el motivo del catálogo 10 (intereses por mora, aumento en el valor, penalidades…).
- **Reglas:** REG-007, REG-019, REG-032, REG-070 a REG-072 y REG-074.
- **Endpoint:** `POST /notas-debito`.
- **Contraste con Nubefact:** **no se capturó** en el DEMO. Según su manual, `tipo_de_nota_de_debito` usa una numeración propia que no coincide con el catálogo 10 (DISC-15).

## CU-05 Comunicar baja (2 pasos)

- **Actor:** administrador. **Precondiciones:** el comprobante está `ACEPTADO` (REG-124) y dentro de plazo (REG-111, PENDIENTE).
- **Flujo:** (1) se eligen los documentos y el motivo → el sistema genera `RA-<Fecha>-#####`, lo firma y lo envía → 202 con ticket. (2) Se consulta el estado → `ACEPTADA` o `RECHAZADA` → los documentos pasan a `ANULADO`.
- **Alternos:** el ticket sigue en proceso → `EN_PROCESO` con `Retry-After`. Rechazo → los documentos siguen `ACEPTADO` y se registra el motivo.
- **Reglas:** REG-111 y REG-121 a REG-124.
- **Endpoints:** `POST /comunicaciones-baja`, `GET /comunicaciones-baja/{id}`.
- **Contraste con Nubefact:** coincide con los «2 pasos» y los filtros Aceptadas, Pendientes y Rechazadas (ENT-06 §8) y con las operaciones 3 y 4 de su API.

## CU-06 Enviar resumen diario

- **Actor:** contador o planificador. **Precondición:** hay boletas o notas de boleta con una fecha de referencia determinada.
- **Flujo:** se elige la fecha → el sistema agrupa los ítems (estado, catálogo 19 PENDIENTE), genera `RC-<Fecha>-#####`, lo firma y lo envía → ticket → consulta → las boletas pasan a `ACEPTADO`.
- **Reglas:** REG-111 y REG-120 a REG-124.
- **Endpoints:** `POST /resumenes-diarios`, `GET /resumenes-diarios/{id}`.
- **Contraste con Nubefact:** existe el módulo «Resúmenes de Boletas», pero **no se capturó**.

## CU-07 Gestionar series y correlativos

- **Actor:** administrador. **Precondición:** el establecimiento está registrado.
- **Flujo:** se lista por local → se crea una serie (F### o B###) para el tipo y sus notas → (Android) se reservan series de contingencia por dispositivo.
- **Alternos:** la serie ya existe → 409. Formato inválido → 422.
- **Reglas:** REG-030, REG-031, REG-033 a REG-037 y REG-170.
- **Endpoints:** `GET /series`, `POST /series`, `POST /series/contingencia/asignaciones`.
- **Contraste con Nubefact:** las series cuelgan del **local**, las notas reutilizan la serie de su documento (F o B) y hay series de contingencia numéricas (ENT-06 §6). Se adopta el mismo modelo.

## CU-08 Consultar catálogos

- **Actor:** cualquiera, o la UI al cargar las listas.
- **Flujo:** se pide el índice o el catálogo N → se devuelven los ítems con la advertencia de fuente no oficial.
- **Endpoints:** `GET /catalogos`, `GET /catalogos/{numero}`.
- **Contraste con Nubefact:** la UI muestra listas con el código entre corchetes, por ejemplo «VENTA INTERNA [01]». Ojo: allí el tipo de operación aparece con 2 dígitos, mientras que el catálogo 51 tiene 4 (DISC-06).

## CU-09 Validar RUC o documento de identidad

- **Actor:** vendedor o administrador (al registrar un cliente o emitir).
- **Flujo:** se ingresa el RUC → se valida el formato (REG-040) y el dígito verificador (REG-041, PENDIENTE) → con conexión, se consulta el padrón (REG-046) y se autocompletan la razón social y la dirección.
- **Alternos:** sin conexión → solo formato. Padrón caído → 503 (la emisión puede continuar con advertencia).
- **Endpoint:** `GET /validaciones/ruc/{ruc}`.
- **Contraste con Nubefact:** el botón **EXTRAER** en «Entidades» parece autocompletar los datos (ENT-06 §5, por confirmar).

## CU-10 Importar el legado

- **Actor:** administrador. **Precondición:** el archivo de fichas está en CSV con las columnas `fecha,ingreso,salida,producto,nro_documento`.
- **Flujo:** se sube el archivo en modo SIMULACIÓN → se revisa el reporte (incidencias por fila y regla) → se corrigen las fichas en cuarentena → se importa en modo DEFINITIVO → conciliación.
- **Alternos:** el mismo archivo otra vez → replay idempotente por hash. Conciliación descuadrada → `FALLIDO`.
- **Reglas:** REG-130 a REG-135 (ADR-005, [mapeo-legado.md](06-migracion/mapeo-legado.md)).
- **Endpoints:** `POST /importaciones-legado`, `GET /importaciones-legado/{id}`.
- **Contraste con Nubefact:** no tiene equivalente; es una necesidad propia de ABC.

## CU-11 Generar registros 14.1, 8.1 y 12.1

- **Actor:** contador. **Precondición:** el período está cerrado.
- **Flujo:** se elige el formato y el período (y el establecimiento para el 12.1) → el sistema proyecta los datos de los comprobantes (14.1), las compras (8.1) o los movimientos (12.1) → se descarga.
- **Reglas:** REG-140 a REG-142 (**PENDIENTE**: estructura oficial, ENT-07).
- **Endpoint:** `GET /registros/{formato}/{periodo}`.
- **Contraste con Nubefact:** solo hay «Descarga Excel» del consolidado y un menú de Reportes; no se vio un registro formal.

## CU-12 Reintentar envío y sincronizar el dispositivo

- **Actor:** planificador o vendedor (Android).
- **Flujo:** (a) Reintento: hay comprobantes `EMITIDO` o `ENVIADO` sin CDR → se reenvían con la misma clave. (b) Sincronización: el dispositivo recupera la conexión → envía el lote de contingencia → el nodo firma y envía → resultado por elemento (207).
- **Reglas:** REG-033, REG-034, REG-110, REG-160 y REG-170 (ADR-006).
- **Endpoints:** `POST /comprobantes/{id}/envios`, `POST /sincronizacion/lotes`.
- **Contraste con Nubefact:** la columna «Offline», las series de contingencia (§6) y el campo `generado_por_contingencia` del manual.

## CU-13 Gestionar productos

- **Actor:** administrador.
- **Flujo:** se registra u homologa un producto (código interno, nombre, tipo, **código de producto SUNAT**, unidad del cat. 03, afectación del cat. 07 y sistema de ISC del cat. 08) → se listan los provisionales del legado (`requiereHomologacion`).
- **Reglas:** REG-012, REG-016, REG-017, REG-027 y REG-132.
- **Endpoints:** `GET /productos`, `POST /productos`.
- **Contraste con Nubefact:** el «Catálogo» tiene los campos obligatorios Categoría, Tipo, Código interno y Nombre, y como opcionales el código SUNAT, la afectación y los precios (ENT-06 §4). Aquí la **unidad** es obligatoria (MT-050) y el ISC es explícito.
