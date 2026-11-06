package pe.abc.fe

import org.w3c.dom.Document
import pe.abc.fe.aplicacion.GenerarXmlComprobanteUseCase
import pe.abc.fe.aplicacion.ParametrosTributariosPort
import pe.abc.fe.dominio.Adquirente
import pe.abc.fe.dominio.AfectacionIgv
import pe.abc.fe.dominio.Comprobante
import pe.abc.fe.dominio.Emisor
import pe.abc.fe.dominio.Leyenda
import pe.abc.fe.dominio.LineaDetalle
import pe.abc.fe.dominio.TipoComprobante
import pe.abc.fe.ubl.GeneradorUblInvoice
import pe.abc.fe.ubl.ValidadorXsdUbl
import java.io.ByteArrayInputStream
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalTime
import javax.xml.XMLConstants
import javax.xml.namespace.NamespaceContext
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.xpath.XPathConstants
import javax.xml.xpath.XPathFactory

/**
 * Datos de prueba FICTICIOS (RUC, nombres y montos inventados).
 * Las tasas son ILUSTRATIVAS de prueba, no verificadas en fuente oficial (SUP-04, DISC-14):
 * el código nunca las fija; se inyectan por ParametrosTributariosPort (RNF-06).
 */
object Fixtures {
    val FECHA: LocalDate = LocalDate.of(2026, 10, 27)
    val TASA_IGV_PRUEBA = BigDecimal("18.00")
    val ICBPER_PRUEBA = BigDecimal("0.50")

    val parametros = object : ParametrosTributariosPort {
        override fun tasaIgv(fecha: LocalDate) = TASA_IGV_PRUEBA
        override fun montoUnitarioIcbper(fecha: LocalDate) = ICBPER_PRUEBA
    }
    val parametrosSinConfigurar = object : ParametrosTributariosPort {
        override fun tasaIgv(fecha: LocalDate): BigDecimal? = null
        override fun montoUnitarioIcbper(fecha: LocalDate): BigDecimal? = null
    }

    val generador = GeneradorUblInvoice()
    val validadorXsd = ValidadorXsdUbl()
    fun casoDeUso(p: ParametrosTributariosPort = parametros) = GenerarXmlComprobanteUseCase(p, generador, validadorXsd)

    val emisor = Emisor(
        ruc = "20000000001",
        razonSocial = "ABC SOFTWARE CORP S.A.C. (FICTICIO)",
        nombreComercial = "ABC MAYORISTA",
        codigoEstablecimiento = "0000",
        ubigeo = "150101",
    )
    val clienteRuc = Adquirente("6", "20000000002", "BODEGA FICTICIA LOS ANDES S.A.C.")
    val clienteDni = Adquirente("1", "00000001", "CLIENTE FICTICIO")

    val arroz = LineaDetalle(
        descripcion = "ARROZ SUPERIOR SACO 50 KG",
        cantidad = BigDecimal("10"),
        unidadMedida = "BG",
        valorUnitario = BigDecimal("100.00"),
        afectacionIgv = AfectacionIgv.GRAVADO_ONEROSA,
        codigoProducto = "ARR-050",
        codigoProductoSunat = "50221101",
    )

    fun factura(vararg lineas: LineaDetalle = arrayOf(arroz)) = Comprobante(
        tipo = TipoComprobante.FACTURA,
        serie = "F001",
        correlativo = 1,
        fechaEmision = FECHA,
        horaEmision = LocalTime.of(10, 15),
        emisor = emisor,
        adquirente = clienteRuc,
        lineas = lineas.toList(),
        leyendas = listOf(Leyenda("1000", "MIL CIENTO OCHENTA CON 00/100 SOLES")),
    )

    fun boleta(vararg lineas: LineaDetalle = arrayOf(arroz)) = factura(*lineas).copy(
        tipo = TipoComprobante.BOLETA, serie = "B001", adquirente = clienteDni, leyendas = emptyList(),
    )
}

/** Consultas XPath sobre el XML generado, con los prefijos UBL. */
class XmlUbl(xml: String) {
    private val doc: Document = DocumentBuilderFactory.newInstance().apply {
        isNamespaceAware = true
        setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)
    }.newDocumentBuilder().parse(ByteArrayInputStream(xml.toByteArray(Charsets.UTF_8)))

    private val xpath = XPathFactory.newInstance().newXPath().apply {
        namespaceContext = object : NamespaceContext {
            val ns = mapOf(
                "inv" to "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
                "cac" to "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                "cbc" to "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "ext" to "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            )
            override fun getNamespaceURI(prefix: String) = ns[prefix] ?: XMLConstants.NULL_NS_URI
            override fun getPrefix(uri: String): String? = ns.entries.firstOrNull { it.value == uri }?.key
            override fun getPrefixes(uri: String) = listOfNotNull(getPrefix(uri)).iterator()
        }
    }

    /** Texto del nodo o atributo (vacío si no existe). Usar "inv:" para la raíz: /inv:Invoice/... */
    fun texto(expr: String): String = xpath.evaluate(expr, doc, XPathConstants.STRING) as String
    fun cantidad(expr: String): Int = (xpath.evaluate("count($expr)", doc, XPathConstants.NUMBER) as Double).toInt()
    fun decimal(expr: String): BigDecimal = BigDecimal(texto(expr))
}
