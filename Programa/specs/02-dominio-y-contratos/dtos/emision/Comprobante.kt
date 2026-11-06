// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de comprobante/nota/linea-detalle/tributo/totales/forma-pago/adquirente/serie .schema.yaml
package pe.abc.fe.emision

import pe.abc.fe.comun.*
import pe.abc.fe.integracion.RespuestaSunatDto

enum class EstadoComprobante { BORRADOR, EMITIDO, ENVIADO, ACEPTADO, OBSERVADO, RECHAZADO, ANULADO } // interno (RF-17)

data class AdquirenteDto(
    val tipoDocumento: CodigoCatalogo,  // MT-079 (cat. 06)  TODO(spec: REG-015) TODO(spec: REG-042) TODO(spec: REG-043)
    val numeroDocumento: String,        // MT-078            TODO(spec: REG-044) TODO(spec: REG-045)
    val razonSocial: String,            // MT-088            TODO(spec: REG-100)
    val direccion: Direccion?,          // interno
    val email: String?,                 // interno
)

data class LeyendaDto(
    val codigo: CodigoCatalogo, // MT-012 (cat. 52)  TODO(spec: REG-025)
    val texto: String,          // MT-011            TODO(spec: REG-008)
)

data class GuiaRelacionadaDto(
    val tipo: CodigoCatalogo,   // MT-017 (cat. 01)
    val serieNumero: String,    // MT-016
)

data class DocumentoRelacionadoDto(
    val tipo: String,           // MT-019 (cat. 12, PENDIENTE)  TODO(spec: REG-026)
    val numero: String,         // MT-018
)

data class TributoDto(
    val codigoTributo: CodigoCatalogo, // MT-066 / MT-038 (cat. 05)  TODO(spec: REG-014)
    val base: Monto?,                  // MT-060 / MT-035
    val tasa: Porcentaje?,             // MT-063  TODO(spec: REG-051) valor desde ParametrosTributariosPort
    val monto: Monto,                  // MT-061 / MT-036  TODO(spec: REG-050) TODO(spec: REG-052) TODO(spec: REG-054)
)

data class PrecioUnitarioDto(
    val monto: PrecioUnitario,      // MT-052
    val tipoPrecio: CodigoCatalogo, // MT-053 (cat. 16)  TODO(spec: REG-020) TODO(spec: REG-055)
)

/** ISC. El catálogo 08 (sistema de cálculo) es el punto clave del caso. */
data class IscDto(
    val sistemaCalculo: CodigoCatalogo, // MT-065 (cat. 08)  TODO(spec: REG-017)
    val base: Monto?,                   // MT-060 (readOnly)
    val tasa: Porcentaje?,              // MT-063 (readOnly, ParametrosTributariosPort)
    val monto: Monto?,                  // MT-061 (readOnly)  TODO(spec: REG-052) TODO(spec: REG-053) TODO(spec: REG-059)
)

/** ICBPER: PENDIENTE de norma (DISC-14). */
data class IcbperDto(
    val cantidadBolsas: Int,     // MT-191
    val montoUnitario: Monto?,   // MT-192 (readOnly)  TODO(spec: REG-054) parámetro vigente
    val monto: Monto?,           // MT-190 (readOnly)  TODO(spec: REG-059)
)

data class LineaDetalleDto(
    val numeroOrden: Int,                         // MT-048  TODO(spec: REG-005)
    val productoId: String?,                      // interno
    val codigoProducto: String?,                  // MT-070
    val codigoProductoSunat: String?,             // MT-071  TODO(spec: REG-027)
    val descripcion: String,                      // MT-069  TODO(spec: REG-100)
    val cantidad: Cantidad,                       // MT-049
    val unidadMedida: CodigoCatalogo,             // MT-050 (cat. 03)  TODO(spec: REG-012)
    val valorUnitario: PrecioUnitario,            // MT-072
    val precioUnitario: PrecioUnitarioDto?,       // MT-052
    val valorVenta: Monto?,                       // MT-051 (readOnly)  TODO(spec: REG-060) TODO(spec: REG-059)
    val cargosDescuentos: List<CargoDescuento>,   // MT-054..MT-058  TODO(spec: REG-024)
    val afectacionIgv: CodigoCatalogo,            // MT-064 (cat. 07)  TODO(spec: REG-016) TODO(spec: REG-022)
    val isc: IscDto?,                             // MT-065
    val icbper: IcbperDto?,                       // MT-190
    val tributos: List<TributoDto>,               // MT-060 (readOnly)  TODO(spec: REG-058)
    val totalTributos: Monto?,                    // MT-059 (readOnly)
)

data class TotalesDto(
    val totalGravado: Monto?,        // MT-035
    val totalExonerado: Monto?,      // MT-035
    val totalInafecto: Monto?,       // MT-035
    val totalGratuito: Monto?,       // MT-035
    val totalIgv: Monto?,            // MT-036
    val totalIsc: Monto?,            // MT-036
    val totalIcbper: Monto?,         // MT-190
    val totalTributos: Monto?,       // MT-034  TODO(spec: REG-057)
    val valorVenta: Monto?,          // MT-041  TODO(spec: REG-061)
    val precioVenta: Monto?,         // MT-042  TODO(spec: REG-062)
    val descuentosGlobales: Monto?,  // MT-043  TODO(spec: REG-063)
    val otrosCargos: Monto?,         // MT-044  TODO(spec: REG-064)
    val anticipos: MontoAnticipo?,   // MT-045  TODO(spec: REG-065)
    val importeTotal: Monto,         // MT-046  TODO(spec: REG-066) TODO(spec: REG-068)
)

enum class TipoFormaPago { CONTADO, CREDITO } // MT-193 (PENDIENTE de norma)

data class CuotaDto(
    val numero: Int,               // MT-195
    val monto: Monto,              // MT-194
    val fechaVencimiento: Fecha,   // MT-196
)

data class FormaPagoDto(
    val tipo: TipoFormaPago,       // MT-193  TODO(spec: REG-028)
    val montoPendiente: Monto?,    // MT-194
    val cuotas: List<CuotaDto>,    // MT-195  TODO(spec: REG-029)
)

/** Factura (01) o boleta (03). Agregado raíz.
 *  Montos: String decimal (BigDecimal en el dominio), NUNCA Double. Los campos (readOnly) los calcula el núcleo (REG-059). */
data class ComprobanteDto(
    val id: String?,                                   // interno (readOnly)
    val tipoComprobante: CodigoCatalogo,               // MT-010 (cat. 01)  TODO(spec: REG-004) TODO(spec: REG-010)
    val serie: SerieCodigo,                            // MT-006  TODO(spec: REG-030) TODO(spec: REG-031)
    val correlativo: Correlativo?,                     // MT-006 (readOnly)  TODO(spec: REG-034) TODO(spec: REG-035)
    val fechaEmision: Fecha,                           // MT-007  TODO(spec: REG-080)
    val horaEmision: Hora?,                            // MT-008  TODO(spec: REG-082)
    val fechaVencimiento: Fecha?,                      // MT-009  TODO(spec: REG-081)
    val tipoOperacion: CodigoCatalogo,                 // MT-087 (cat. 51)  TODO(spec: REG-021) TODO(spec: REG-023)
    val moneda: CodigoCatalogo,                        // MT-013 (cat. 02)  TODO(spec: REG-011) TODO(spec: REG-069)
    val establecimientoCodigo: CodigoEstablecimiento,  // MT-076  TODO(spec: REG-036)
    val emisorRuc: Ruc?,                               // MT-073 (readOnly)
    val adquirente: AdquirenteDto,                     // MT-078
    val leyendas: List<LeyendaDto>,                    // MT-011
    val ordenCompra: String?,                          // MT-015
    val guias: List<GuiaRelacionadaDto>,               // MT-016
    val documentosRelacionados: List<DocumentoRelacionadoDto>, // MT-018
    val formaPago: FormaPagoDto?,                      // MT-193
    val cargosDescuentos: List<CargoDescuento>,        // MT-029
    val lineas: List<LineaDetalleDto>,                 // MT-048  TODO(spec: REG-006) TODO(spec: REG-009)
    val tributos: List<TributoDto>,                    // MT-035 (readOnly)  TODO(spec: REG-057)
    val totales: TotalesDto?,                          // MT-046 (readOnly)  TODO(spec: REG-059)
    val estado: EstadoComprobante?,                    // interno (readOnly)
    val firma: FirmaDigitalDto?,                       // MT-001 (readOnly)  TODO(spec: REG-090)
    val respuestaSunat: RespuestaSunatDto?,            // interno (readOnly)
    val origen: Origen?,                               // interno (readOnly)
)

data class MotivoNotaDto(
    val codigo: CodigoCatalogo, // MT-097 (cat. 09 NC / cat. 10 ND)  TODO(spec: REG-018) TODO(spec: REG-019)
    val descripcion: String,    // MT-098  TODO(spec: REG-074)
)

/** Nota de crédito (07) o débito (08). Agregado raíz. */
data class NotaDto(
    val id: String?,                                  // interno
    val tipoComprobante: CodigoCatalogo,              // MT-010
    val serie: SerieCodigo,                           // MT-093  TODO(spec: REG-032)
    val correlativo: Correlativo?,                    // MT-093
    val fechaEmision: Fecha,                          // MT-094
    val horaEmision: Hora?,                           // MT-008
    val tipoOperacion: CodigoCatalogo?,               // MT-122
    val moneda: CodigoCatalogo,                       // MT-095
    val establecimientoCodigo: CodigoEstablecimiento, // MT-076
    val emisorRuc: Ruc?,                              // MT-101
    val adquirente: AdquirenteDto,                    // MT-102  TODO(spec: REG-073)
    val documentoAfectado: ReferenciaDocumento,       // MT-096  TODO(spec: REG-070) TODO(spec: REG-071) TODO(spec: REG-072)
    val motivo: MotivoNotaDto,                        // MT-097
    val leyendas: List<LeyendaDto>,                   // MT-011
    val lineas: List<LineaDetalleDto>,                // MT-105
    val tributos: List<TributoDto>,                   // MT-103 (readOnly)
    val totales: TotalesDto?,                         // MT-104 (readOnly)
    val estado: EstadoComprobante?,                   // interno
    val firma: FirmaDigitalDto?,                      // MT-090
    val respuestaSunat: RespuestaSunatDto?,           // interno
)

/** Agregado Serie: única fuente del correlativo. */
data class SerieDto(
    val id: String?,                                  // interno
    val establecimientoCodigo: CodigoEstablecimiento, // MT-076
    val tiposComprobante: List<String>,               // MT-010   TODO(spec: REG-037)
    val serie: SerieCodigo,                           // MT-006
    val ultimoCorrelativo: Long?,                     // MT-006 (readOnly)  TODO(spec: REG-035)
    val contingencia: Boolean,                        // interno  TODO(spec: REG-033) TODO(spec: REG-170)
    val dispositivoId: String?,                       // interno (ADR-006)
    val activa: Boolean,                              // interno
)
