package pe.abc.fe.dominio

import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalTime

/**
 * Modelo de dominio de la factura y la boleta (specs/02-dominio-y-contratos/modelo-dominio.md).
 * Solo datos de origen: los montos calculados (valor de venta, tributos, totales) los produce
 * [CalculadoraComprobante] y nunca vienen del cliente (REG-059). Montos siempre en BigDecimal.
 */
data class Comprobante(
    val tipo: TipoComprobante,
    val serie: String,                       // MT-006  REG-030 / REG-031
    val correlativo: Long,                   // MT-006  REG-035
    val fechaEmision: LocalDate,             // MT-007
    val emisor: Emisor,
    val adquirente: Adquirente,
    val lineas: List<LineaDetalle>,          // MT-048  REG-006
    val horaEmision: LocalTime? = null,      // MT-008
    val fechaVencimiento: LocalDate? = null, // MT-009  REG-081
    val moneda: String = "PEN",              // MT-013  catálogo 02
    val tipoOperacion: String = "0101",      // MT-087  catálogo 51 -> InvoiceTypeCode/@listID
    val formaPago: FormaPago = FormaPago.Contado,
    val leyendas: List<Leyenda> = emptyList(),
) {
    /** Serie-número, p. ej. F001-1 (cbc:ID). */
    val numero: String get() = "$serie-$correlativo"
}

data class Emisor(
    val ruc: String,                          // MT-073  REG-040
    val razonSocial: String,                  // MT-075
    val nombreComercial: String? = null,      // MT-021
    val codigoEstablecimiento: String = "0000", // MT-076  REG-036
    val ubigeo: String? = null,               // MT-077  REG-038
)

data class Adquirente(
    val tipoDocumento: String,                // MT-079  catálogo 06
    val numeroDocumento: String,              // MT-078
    val razonSocial: String,                  // MT-088
)

data class LineaDetalle(
    val descripcion: String,                  // MT-069
    val cantidad: BigDecimal,                 // MT-049
    val unidadMedida: String,                 // MT-050  catálogo 03
    val valorUnitario: BigDecimal,            // MT-072  sin impuestos
    val afectacionIgv: AfectacionIgv,         // MT-064  catálogo 07
    val codigoProducto: String? = null,       // MT-070
    val codigoProductoSunat: String? = null,  // MT-071  n8 UNSPSC
    val isc: Isc? = null,                     // MT-065  catálogo 08
    val bolsasPlastico: Int = 0,              // MT-191  ICBPER
)

/**
 * ISC de la línea. [tasaOMonto] depende del sistema (catálogo 08):
 *  - AL_VALOR: tasa % sobre el valor de venta.
 *  - MONTO_FIJO: monto por unidad.
 *  - PRECIO_VENTA_PUBLICO: factor % sobre [precioVentaPublico] × cantidad.
 * Las fórmulas son SUPUESTO de diseño (REG-052, PENDIENTE del TUO IGV e ISC); la tasa la da el producto.
 */
data class Isc(
    val sistema: SistemaIsc,
    val tasaOMonto: BigDecimal,
    val precioVentaPublico: BigDecimal? = null,
)

data class Leyenda(val codigo: String, val texto: String) // MT-011/MT-012  catálogo 52

sealed interface FormaPago {
    /** PaymentTerms FormaPago / Contado (MT-193). */
    data object Contado : FormaPago

    /** PaymentTerms FormaPago / Credito + Cuota### (MT-193..MT-196, REG-028, REG-029). */
    data class Credito(val cuotas: List<Cuota>) : FormaPago
}

data class Cuota(val monto: BigDecimal, val fechaVencimiento: LocalDate)
