package pe.abc.fe.dominio

import java.math.BigDecimal
import java.math.RoundingMode

/** Montos de una línea, calculados por el núcleo (REG-059). */
data class LineaCalculada(
    val numeroOrden: Int,
    val linea: LineaDetalle,
    val valorVenta: BigDecimal,          // MT-051  REG-060
    val isc: BigDecimal,                 // MT-061 (tributo 2000)
    val baseIgv: BigDecimal,             // MT-060
    val tasaIgv: BigDecimal,             // MT-063
    val igv: BigDecimal,                 // MT-061 (tributo 1000) o 0 si no es gravada
    val icbper: BigDecimal,              // MT-190
    val montoUnitarioIcbper: BigDecimal, // MT-192
    val precioUnitario: BigDecimal,      // MT-052  con impuestos
) {
    val totalTributos: BigDecimal get() = isc + igv + icbper // MT-059
}

/** Subtotal de cabecera por tributo (MT-035, MT-036, REG-057). */
data class SubtotalTributo(val tributo: Tributo, val base: BigDecimal, val monto: BigDecimal)

data class Totales(
    val valorVenta: BigDecimal,     // MT-041  REG-061
    val totalTributos: BigDecimal,  // MT-034  REG-057
    val precioVenta: BigDecimal,    // MT-042  REG-062
    val importeTotal: BigDecimal,   // MT-046  REG-066
)

data class ComprobanteCalculado(
    val comprobante: Comprobante,
    val lineas: List<LineaCalculada>,
    val subtotales: List<SubtotalTributo>,
    val totales: Totales,
)

/**
 * Calcula tributos y totales. Las tasas NO están en el código: vienen de [ParametrosTributarios] (RNF-06).
 * Redondeo HALF_UP a 2 decimales por monto (REG-067, REG-068).
 */
class CalculadoraComprobante(private val parametros: ParametrosTributarios) {

    fun calcular(c: Comprobante): ComprobanteCalculado {
        val tasaIgv by lazy { parametros.tasaIgv(c.fechaEmision) ?: throw ParametroNoConfiguradoException("REG-050", "IGV_TASA") }
        val icbperUnitario by lazy { parametros.montoUnitarioIcbper(c.fechaEmision) ?: throw ParametroNoConfiguradoException("REG-054", "ICBPER_MONTO_UNITARIO") }

        val lineas = c.lineas.mapIndexed { i, l ->
            val valorVenta = dosDecimales(l.cantidad * l.valorUnitario)
            val isc = l.isc?.let { dosDecimales(calcularIsc(it, l, valorVenta)) } ?: BigDecimal.ZERO.setScale(2)
            val gravada = l.afectacionIgv == AfectacionIgv.GRAVADO_ONEROSA
            // SUPUESTO (REG-053, PENDIENTE): la base del IGV incluye el ISC.
            val baseIgv = valorVenta + isc
            val tasa = if (gravada) tasaIgv else BigDecimal.ZERO
            val igv = if (gravada) dosDecimales(porcentaje(baseIgv, tasa)) else BigDecimal.ZERO.setScale(2)
            val unitarioBolsa = if (l.bolsasPlastico > 0) icbperUnitario else BigDecimal.ZERO
            val icbper = dosDecimales(unitarioBolsa * BigDecimal(l.bolsasPlastico))
            val precioUnitario = (valorVenta + isc + igv)
                .divide(l.cantidad, 10, RoundingMode.HALF_UP).stripTrailingZeros().let { if (it.scale() < 2) it.setScale(2) else it }
            LineaCalculada(i + 1, l, valorVenta, isc, dosDecimales(baseIgv), tasa, igv, icbper, unitarioBolsa, precioUnitario)
        }

        val subtotales = buildList {
            val porAfectacion = lineas.groupBy { it.linea.afectacionIgv.tributo }
            porAfectacion[Tributo.IGV]?.let { ls -> add(SubtotalTributo(Tributo.IGV, suma(ls) { it.baseIgv }, suma(ls) { it.igv })) }
            listOf(Tributo.EXONERADO, Tributo.INAFECTO, Tributo.EXPORTACION).forEach { t ->
                porAfectacion[t]?.let { ls -> add(SubtotalTributo(t, suma(ls) { it.valorVenta }, BigDecimal.ZERO.setScale(2))) }
            }
            lineas.filter { it.isc.signum() > 0 }.takeIf { it.isNotEmpty() }?.let { ls ->
                add(SubtotalTributo(Tributo.ISC, suma(ls) { it.valorVenta }, suma(ls) { it.isc }))
            }
            lineas.filter { it.icbper.signum() > 0 }.takeIf { it.isNotEmpty() }?.let { ls ->
                add(SubtotalTributo(Tributo.ICBPER, BigDecimal.ZERO.setScale(2), suma(ls) { it.icbper }))
            }
        }

        val valorVenta = suma(lineas) { it.valorVenta }
        val totalTributos = suma(subtotales.map { it.monto })
        val precioVenta = valorVenta + totalTributos
        return ComprobanteCalculado(c, lineas, subtotales, Totales(valorVenta, totalTributos, precioVenta, precioVenta))
    }

    /** Catálogo 08. Fórmulas: SUPUESTO de diseño (REG-052 PENDIENTE de las tasas y apéndices del TUO). */
    private fun calcularIsc(isc: Isc, l: LineaDetalle, valorVenta: BigDecimal): BigDecimal = when (isc.sistema) {
        SistemaIsc.AL_VALOR -> porcentaje(valorVenta, isc.tasaOMonto)
        SistemaIsc.MONTO_FIJO -> l.cantidad * isc.tasaOMonto
        SistemaIsc.PRECIO_VENTA_PUBLICO -> porcentaje(l.cantidad * isc.precioVentaPublico!!, isc.tasaOMonto)
    }

    private companion object {
        val CIEN = BigDecimal(100)
        fun dosDecimales(v: BigDecimal): BigDecimal = v.setScale(2, RoundingMode.HALF_UP)
        fun porcentaje(base: BigDecimal, tasa: BigDecimal): BigDecimal = (base * tasa).divide(CIEN, 10, RoundingMode.HALF_UP)
        fun suma(valores: List<BigDecimal>): BigDecimal = valores.fold(BigDecimal.ZERO.setScale(2)) { a, b -> a + b }
        fun <T> suma(xs: List<T>, f: (T) -> BigDecimal): BigDecimal = suma(xs.map(f))
    }
}

/**
 * Tasas y montos tributarios con vigencia (RNF-06). Interfaz del dominio: la implementa el adaptador
 * de parámetros (ParametrosTributariosPort en la capa de aplicación). null = no configurado (PENDIENTE).
 */
interface ParametrosTributarios {
    fun tasaIgv(fecha: java.time.LocalDate): BigDecimal?
    fun montoUnitarioIcbper(fecha: java.time.LocalDate): BigDecimal?
}
