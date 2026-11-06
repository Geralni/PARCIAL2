package pe.abc.fe.demo

import pe.abc.fe.aplicacion.GenerarXmlComprobanteUseCase
import pe.abc.fe.aplicacion.ParametrosTributariosPort
import pe.abc.fe.dominio.Adquirente
import pe.abc.fe.dominio.AfectacionIgv
import pe.abc.fe.dominio.Comprobante
import pe.abc.fe.dominio.Cuota
import pe.abc.fe.dominio.Emisor
import pe.abc.fe.dominio.FormaPago
import pe.abc.fe.dominio.Isc
import pe.abc.fe.dominio.Leyenda
import pe.abc.fe.dominio.LineaDetalle
import pe.abc.fe.dominio.SistemaIsc
import pe.abc.fe.dominio.TipoComprobante
import pe.abc.fe.ubl.GeneradorUblInvoice
import pe.abc.fe.ubl.ValidadorXsdUbl
import java.io.File
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalTime

/**
 * Demostración: genera una factura y una boleta FICTICIAS en ./ejemplos-generados/.
 * Las tasas son ILUSTRATIVAS (no verificadas, SUP-04): en producción vienen de ParametrosTributariosPort.
 * Uso: mvn -q process-classes exec:java
 */
fun main() {
    val parametros = object : ParametrosTributariosPort {
        override fun tasaIgv(fecha: LocalDate) = BigDecimal("18.00")
        override fun montoUnitarioIcbper(fecha: LocalDate) = BigDecimal("0.50")
    }
    val casoDeUso = GenerarXmlComprobanteUseCase(parametros, GeneradorUblInvoice(), ValidadorXsdUbl())
    val emisor = Emisor("20000000001", "ABC SOFTWARE CORP S.A.C. (FICTICIO)", "ABC MAYORISTA", "0000", "150101")
    val arroz = LineaDetalle("ARROZ SUPERIOR SACO 50 KG", BigDecimal("10"), "BG", BigDecimal("100.00"),
        AfectacionIgv.GRAVADO_ONEROSA, "ARR-050", "50221101")
    val bebida = LineaDetalle("BEBIDA FICTICIA SUJETA A ISC LATA 355 ML", BigDecimal("24"), "NIU", BigDecimal("2.50"),
        AfectacionIgv.GRAVADO_ONEROSA, "BEB-355", isc = Isc(SistemaIsc.AL_VALOR, BigDecimal("10.00")))

    val factura = Comprobante(
        tipo = TipoComprobante.FACTURA, serie = "F001", correlativo = 1, fechaEmision = LocalDate.of(2026, 10, 27),
        horaEmision = LocalTime.of(10, 15), fechaVencimiento = LocalDate.of(2026, 12, 26),
        emisor = emisor, adquirente = Adquirente("6", "20000000002", "BODEGA FICTICIA LOS ANDES S.A.C."),
        lineas = listOf(arroz, bebida),
        formaPago = FormaPago.Credito(listOf(Cuota(BigDecimal("628.94"), LocalDate.of(2026, 11, 26)), Cuota(BigDecimal("628.94"), LocalDate.of(2026, 12, 26)))),
        leyendas = listOf(Leyenda("1000", "MIL DOSCIENTOS CINCUENTA Y SIETE CON 88/100 SOLES")),
    )
    val boleta = factura.copy(
        tipo = TipoComprobante.BOLETA, serie = "B001", fechaVencimiento = null, formaPago = FormaPago.Contado, leyendas = emptyList(),
        adquirente = Adquirente("1", "00000001", "CLIENTE FICTICIO"), lineas = listOf(arroz.copy(cantidad = BigDecimal("2"), bolsasPlastico = 1)),
    )

    val carpeta = File("ejemplos-generados").apply { mkdirs() }
    for (c in listOf(factura, boleta)) {
        val r = casoDeUso.ejecutar(c)
        File(carpeta, r.nombreArchivo).writeText(r.xml, Charsets.UTF_8)
        println("OK ${r.nombreArchivo}  total=${r.calculado.totales.importeTotal} ${c.moneda}  (válido contra UBL-Invoice-2.1.xsd)")
    }
}
