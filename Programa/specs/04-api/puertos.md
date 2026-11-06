# Puertos de entrada y de salida

> **Entregable 3 (parte B).** En una app nativa, **el puerto es el contrato**. La UI de Windows y Android lo invoca en el mismo proceso, y [`openapi.yaml`](openapi.yaml) es su *binding* HTTP (el adaptador Ktor). Las firmas son **interfaces Kotlin sin implementación**. Los tipos son los de [`../02-dominio-y-contratos/dtos/`](../02-dominio-y-contratos/dtos/).
> `Resultado<T>` = `Exito(T)` | `Fallo(ProblemaDto)` (RFC 9457, `problema.schema.yaml`). Ningún puerto lanza excepciones de negocio.

## 1. Puertos de entrada (casos de uso) ↔ binding HTTP

| Puerto de entrada · método | Caso de uso | `operationId` | HTTP |
|---|---|---|---|
| `EmitirComprobanteUseCase.emitir` | CU-01 | `emitirComprobante` | `POST /comprobantes` |
| `ConsultarComprobanteUseCase.buscar` | CU-02 | `buscarComprobantes` | `GET /comprobantes` |
| `ConsultarComprobanteUseCase.consultar` | CU-02 | `consultarComprobante` | `GET /comprobantes/{id}` |
| `ConsultarComprobanteUseCase.obtenerXml` | CU-02 | `descargarXml` | `GET /comprobantes/{id}/xml` |
| `ConsultarComprobanteUseCase.obtenerCdr` | CU-02 | `descargarCdr` | `GET /comprobantes/{id}/cdr` |
| `EmitirNotaUseCase.emitirCredito` | CU-03 | `emitirNotaCredito` | `POST /notas-credito` |
| `EmitirNotaUseCase.emitirDebito` | CU-04 | `emitirNotaDebito` | `POST /notas-debito` |
| `ComunicarBajaUseCase.comunicar` | CU-05 | `crearComunicacionBaja` | `POST /comunicaciones-baja` → 202 + ticket |
| `ComunicarBajaUseCase.consultarEstado` | CU-05 | `consultarEstadoBaja` | `GET /comunicaciones-baja/{id}` |
| `EnviarResumenDiarioUseCase.enviar` | CU-06 | `crearResumenDiario` | `POST /resumenes-diarios` → 202 |
| `EnviarResumenDiarioUseCase.consultarEstado` | CU-06 | `consultarEstadoResumen` | `GET /resumenes-diarios/{id}` |
| `GestionarSeriesUseCase.listar` / `crear` / `asignarContingencia` | CU-07 | `listarSeries`, `crearSerie`, `asignarSeriesContingencia` | `GET` y `POST /series`, `POST /series/contingencia/asignaciones` |
| `ConsultarCatalogoUseCase.listar` / `obtener` | CU-08 | `listarCatalogos`, `obtenerCatalogo` | `GET /catalogos`, `GET /catalogos/{numero}` |
| `ValidarDocumentoIdentidadUseCase.validarRuc` | CU-09 | `validarRuc` | `GET /validaciones/ruc/{ruc}` |
| `ImportarLegadoUseCase.importar` / `consultar` | CU-10 | `importarLegado`, `consultarImportacion` | `POST /importaciones-legado`, `GET /importaciones-legado/{id}` |
| `GenerarRegistroUseCase.generar` | CU-11 | `generarRegistro` | `GET /registros/{formato}/{periodo}` |
| `ReintentarEnvioUseCase.reintentar` | CU-12 | `reenviarComprobante` | `POST /comprobantes/{id}/envios` |
| `SincronizarDispositivoUseCase.sincronizar` | CU-12 | `sincronizarLoteOffline` | `POST /sincronizacion/lotes` |
| `GestionarProductosUseCase.listar` / `registrar` | CU-13 | `listarProductos`, `registrarProducto` | `GET` y `POST /productos` |

```kotlin
// shared/application — ESQUELETO, sin implementación.
package pe.abc.fe.application

sealed interface Resultado<out T> {
    data class Exito<T>(val valor: T) : Resultado<T>
    data class Fallo(val problema: ProblemaDto) : Resultado<Nothing>
}

/** Clave de idempotencia (REG-160); null = el núcleo genera una y no garantiza replay. */
@JvmInline value class ClaveIdempotencia(val valor: String)

interface EmitirComprobanteUseCase {
    /** CU-01. REG-003..REG-069, REG-080..REG-090. borrador=true => estado BORRADOR, sin correlativo. */
    suspend fun emitir(cmd: ComprobanteDto, clave: ClaveIdempotencia?, borrador: Boolean = false): Resultado<ComprobanteDto>
}

interface ConsultarComprobanteUseCase {
    suspend fun buscar(filtro: FiltroComprobantes, pagina: Int): Resultado<Pagina<ComprobanteDto>>   // CU-02
    suspend fun consultar(id: String): Resultado<Any /* ComprobanteDto | NotaDto */>
    suspend fun obtenerXml(id: String): Resultado<ByteArray>
    suspend fun obtenerCdr(id: String): Resultado<ByteArray>
}

interface EmitirNotaUseCase {
    suspend fun emitirCredito(cmd: NotaDto, clave: ClaveIdempotencia?): Resultado<NotaDto>    // CU-03
    suspend fun emitirDebito(cmd: NotaDto, clave: ClaveIdempotencia?): Resultado<NotaDto>     // CU-04
}

interface ComunicarBajaUseCase {
    suspend fun comunicar(cmd: ComunicacionBajaDto, clave: ClaveIdempotencia?): Resultado<ComunicacionBajaDto> // CU-05 paso 1
    suspend fun consultarEstado(id: String): Resultado<ComunicacionBajaDto>                                    // CU-05 paso 2
}

interface EnviarResumenDiarioUseCase {
    suspend fun enviar(fechaReferencia: Fecha, establecimiento: CodigoEstablecimiento?, clave: ClaveIdempotencia?): Resultado<ResumenDiarioDto> // CU-06
    suspend fun consultarEstado(id: String): Resultado<ResumenDiarioDto>
}

interface GestionarSeriesUseCase {
    suspend fun listar(establecimiento: CodigoEstablecimiento?, tipo: String?): Resultado<List<SerieDto>> // CU-07
    suspend fun crear(cmd: SerieDto, clave: ClaveIdempotencia?): Resultado<SerieDto>
    suspend fun asignarContingencia(dispositivoId: String, establecimiento: CodigoEstablecimiento, tipos: List<String>): Resultado<List<SerieDto>> // ADR-006
}

interface ConsultarCatalogoUseCase {
    suspend fun listar(): Resultado<List<ResumenCatalogo>>             // CU-08
    suspend fun obtener(numero: String): Resultado<CatalogoDto>
}

interface ValidarDocumentoIdentidadUseCase {
    suspend fun validarRuc(ruc: String): Resultado<ValidacionRucDto>   // CU-09, REG-040..046
}

interface ImportarLegadoUseCase {
    suspend fun importar(archivo: ByteArray, nombre: String, establecimiento: CodigoEstablecimiento, modo: ModoImportacion, clave: ClaveIdempotencia?): Resultado<ImportacionLegadoDto> // CU-10
    suspend fun consultar(id: String): Resultado<ImportacionLegadoDto>
}

interface GenerarRegistroUseCase {
    /** CU-11. formato ∈ {"14.1","8.1","12.1"}. Estructura oficial PENDIENTE (REG-140..142). */
    suspend fun generar(formato: String, periodo: Periodo, establecimiento: CodigoEstablecimiento?): Resultado<Any>
}

interface ReintentarEnvioUseCase {
    suspend fun reintentar(id: String, clave: ClaveIdempotencia?): Resultado<RespuestaSunatDto>       // CU-12
}

interface SincronizarDispositivoUseCase {
    suspend fun sincronizar(dispositivoId: String, lote: List<Pair<ClaveIdempotencia, Any>>): Resultado<List<ResultadoSincronizacion>> // CU-12, ADR-006
}

interface GestionarProductosUseCase {
    suspend fun listar(requiereHomologacion: Boolean?): Resultado<List<ProductoDto>>  // CU-13
    suspend fun registrar(cmd: ProductoDto, clave: ClaveIdempotencia?): Resultado<ProductoDto>
}
```

## 2. Puertos de salida

| Puerto de salida | Responsabilidad | Adaptadores previstos | Microservicio futuro |
|---|---|---|---|
| `ComprobanteRepositoryPort` | Persistir y consultar comprobantes y notas, con su XML y CDR | SQLDelight (SQLite) | Emisión |
| `SerieRepositoryPort` | **Reserva atómica** del siguiente correlativo (REG-034, REG-035) | SQLDelight (transacción `BEGIN IMMEDIATE`) | Emisión |
| `ProductoRepositoryPort`, `MovimientoRepositoryPort` | Productos y movimientos de almacén | SQLDelight | Inventario |
| `CatalogoRepositoryPort` | Leer `catalogs/catNN.json` versionados | Archivos JSON embebidos en la app | Tributación/Catálogos |
| `ParametrosTributariosPort` | Tasas y montos **con vigencia** (RNF-06). Mientras estén PENDIENTE, la emisión real se bloquea | Tabla configurable | Tributación/Catálogos |
| `GeneradorUblPort` | Dominio → XML UBL 2.1 (Invoice, CreditNote, DebitNote, SummaryDocuments, VoidedDocuments) | **Clases generadas desde el XSD UBL con JAXB/`xjc`** (no DOM a mano ni plantillas), ADR-007 | Integración |
| `ValidadorXsdPort` | Validar el XML contra el XSD **antes de firmar** (REG-094) | `javax.xml.validation` con un `Schema` compilado en caché | Integración |
| `FirmadorXmlPort` | XMLDSig enveloped en `ext:ExtensionContent` | `javax.xml.crypto` + almacén de Windows | Integración |
| `ClienteSunatOsePort` | Enviar, recibir el CDR o ticket y consultar el ticket | `OseAdapter` (principal), `SunatDirectoAdapter`, `NubefactAdapter` (con **capa de mapeo** a sus códigos) | Integración |
| `ValidadorRucPort` | Consultar el padrón (razón social, estado y condición) | Servicio SUNAT u OSE (PENDIENTE) | Identidad |
| `ImportadorLegadoPort` | Leer el archivo de fichas → `FichaLegadoDto` (crudo) | CSV y Excel | Migración |
| `GeneradorRegistrosPort` | Exportar 14.1, 8.1 y 12.1 al formato oficial | PENDIENTE (ENT-07) | Registros |
| `ColaEnvioPort` | Cola persistente con *backoff* (ADR-006) | Tabla SQLite | Integración |
| `IdempotenciaPort` | Clave → *hash* del cuerpo y resultado (REG-160) | Tabla SQLite | Transversal |
| `EventosDominioPort` | Publicar `ComprobanteEmitido`, `ComprobanteAceptado`, … | En proceso (Fase 1) → outbox (Fase 2) → bus (Fase 3) | Transversal |
| `RelojPort` | Fecha y hora actuales (para pruebas y para REG-080) | Reloj del sistema | Transversal |

```kotlin
// shared/application/ports/out — ESQUELETO, sin implementación.
interface SerieRepositoryPort {
    /** Atómico: incrementa y devuelve el correlativo. TODO(spec: REG-034) TODO(spec: REG-035) */
    suspend fun reservarSiguiente(serie: SerieCodigo, tipo: String): Correlativo
    suspend fun buscar(establecimiento: CodigoEstablecimiento?, tipo: String?): List<SerieDto>
}
interface GeneradorUblPort { fun generar(doc: Any /* Comprobante|Nota|Resumen|Baja */): ByteArray } // ADR-007: clases xjc
/** REG-094: se invoca ANTES de FirmadorXmlPort. Lista vacía = válido. */
interface ValidadorXsdPort { fun validar(xml: ByteArray, tipoRaiz: String): List<String> }
interface FirmadorXmlPort { fun firmar(xml: ByteArray, certificadoAlias: String): Pair<ByteArray, FirmaDigitalDto> } // REG-090, REG-093
interface ClienteSunatOsePort {
    suspend fun enviarComprobante(nombreArchivo: String, xmlFirmado: ByteArray): RespuestaSunatDto
    suspend fun enviarResumenOBaja(nombreArchivo: String, xmlFirmado: ByteArray): RespuestaSunatDto // devuelve ticket
    suspend fun consultarTicket(ticket: String): RespuestaSunatDto
}
interface ValidadorRucPort { suspend fun consultarPadron(ruc: Ruc): ConsultaPadronDto? }
interface ParametrosTributariosPort { fun vigente(codigo: String, fecha: Fecha, producto: String? = null): ParametroTributarioDto? }
interface CatalogoRepositoryPort { fun codigos(numero: String): Set<String>; fun catalogo(numero: String): CatalogoDto? }
interface ImportadorLegadoPort { fun leer(archivo: ByteArray, nombre: String): Sequence<Pair<Int, FichaLegadoDto>> }
interface GeneradorRegistrosPort { fun exportar(formato: String, registro: Any): ByteArray } // PENDIENTE formato oficial
interface ColaEnvioPort { suspend fun encolar(idDocumento: String, clave: ClaveIdempotencia); suspend fun pendientes(limite: Int): List<String> }
interface IdempotenciaPort { suspend fun buscar(clave: ClaveIdempotencia): RegistroIdempotencia?; suspend fun guardar(r: RegistroIdempotencia) }
interface EventosDominioPort { suspend fun publicar(evento: Any) }
interface RelojPort { fun hoy(): Fecha; fun ahora(): String }
```

## 3. Errores (comunes a la UI y a HTTP)

| `Problema.codigo` | HTTP | Cuándo |
|---|---|---|
| `VALIDACION` | 400 o 422 | 400: el JSON no cumple el schema. 422: se incumple una regla REG-xxx (se listan en `violaciones`) |
| `DUPLICADO` | 409 | Emisor + tipo + serie + correlativo ya existe (REG-034) |
| `IDEMPOTENCIA_CONFLICTO` | 409 | Misma `Idempotency-Key` con otro cuerpo (REG-160) |
| `ESTADO_INVALIDO` | 409 | Transición no permitida, por ejemplo, dar de baja un comprobante RECHAZADO |
| `NO_ENCONTRADO` | 404 | — |
| `PROVEEDOR_NO_DISPONIBLE` | 503 | OSE, SUNAT o padrón caídos. En la emisión **no** se devuelve: el comprobante queda encolado (EMITIDO) |
| `RECHAZADO_SUNAT` | 200 (con el estado del recurso) | Es un resultado de negocio, no un error del API: el comprobante queda RECHAZADO con su CDR |
| `NO_AUTORIZADO` | 401 | — |

**Reintentos:** un cliente que no recibe respuesta reintenta con la **misma** `Idempotency-Key`. El nodo responde 200 con `Idempotent-Replayed: true` y el mismo comprobante y correlativo.
