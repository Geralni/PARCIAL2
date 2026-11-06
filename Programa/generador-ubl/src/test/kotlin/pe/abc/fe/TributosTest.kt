package pe.abc.fe

import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource
import pe.abc.fe.Fixtures.arroz
import pe.abc.fe.Fixtures.casoDeUso
import pe.abc.fe.Fixtures.factura
import pe.abc.fe.dominio.AfectacionIgv
import pe.abc.fe.dominio.Isc
import pe.abc.fe.dominio.LineaDetalle
import pe.abc.fe.dominio.ParametroNoConfiguradoException
import pe.abc.fe.dominio.SistemaIsc
import java.math.BigDecimal
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

/** Tributos de la línea: IGV, afectaciones del catálogo 07, ISC con catálogo 08 (punto clave) e ICBPER. */
@DisplayName("Tributos: IGV, catálogo 07, ISC (catálogo 08) e ICBPER")
class TributosTest {

    private val subtotales = "/inv:Invoice/cac:InvoiceLine[1]/cac:TaxTotal/cac:TaxSubtotal"

    private val bebida = LineaDetalle(
        descripcion = "BEBIDA FICTICIA SUJETA A ISC LATA 355 ML",
        cantidad = BigDecimal("24"),
        unidadMedida = "NIU",
        valorUnitario = BigDecimal("2.50"),
        afectacionIgv = AfectacionIgv.GRAVADO_ONEROSA,
        codigoProducto = "BEB-355",
        isc = Isc(SistemaIsc.AL_VALOR, BigDecimal("10.00")), // tasa de prueba, ficticia
    )

    @Test
    fun `IGV de linea gravada con afectacion 10 y tributo 1000 (MT-061, MT-063, MT-064, REG-050)`() {
        val xml = XmlUbl(casoDeUso().ejecutar(factura()).xml)
        assertEquals("10", xml.texto("$subtotales/cac:TaxCategory/cbc:TaxExemptionReasonCode"))
        assertEquals("urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo07", xml.texto("$subtotales/cac:TaxCategory/cbc:TaxExemptionReasonCode/@listURI"))
        assertEquals("1000", xml.texto("$subtotales/cac:TaxCategory/cac:TaxScheme/cbc:ID"))
        assertEquals("VAT", xml.texto("$subtotales/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode"))
        assertEquals(BigDecimal("18.00"), xml.decimal("$subtotales/cac:TaxCategory/cbc:Percent"))
        assertEquals(BigDecimal("180.00"), xml.decimal("$subtotales/cbc:TaxAmount"))
    }

    @ParameterizedTest(name = "afectación {0}")
    @EnumSource(value = AfectacionIgv::class, names = ["EXONERADO_ONEROSA", "INAFECTO_ONEROSA"])
    fun `lineas no gravadas usan el tributo del catalogo 07 y monto 0 (REG-022, REG-056)`(afectacion: AfectacionIgv) {
        val gen = casoDeUso().ejecutar(factura(arroz.copy(afectacionIgv = afectacion)))
        val xml = XmlUbl(gen.xml)
        assertEquals(afectacion.codigo, xml.texto("$subtotales/cac:TaxCategory/cbc:TaxExemptionReasonCode"))
        assertEquals(afectacion.tributo.codigo, xml.texto("$subtotales/cac:TaxCategory/cac:TaxScheme/cbc:ID"))
        assertEquals(BigDecimal("0.00"), xml.decimal("$subtotales/cbc:TaxAmount"))
        assertEquals(BigDecimal("1000.00"), xml.decimal("/inv:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"))
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @Test
    fun `ISC al valor con sistema 01 en TierRange y base del IGV que incluye el ISC (MT-065, REG-017, REG-052, REG-053)`() {
        val gen = casoDeUso().ejecutar(factura(arroz, bebida))
        val xml = XmlUbl(gen.xml)
        val isc = "/inv:Invoice/cac:InvoiceLine[2]/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:ID='2000']"
        assertEquals("01", xml.texto("$isc/cac:TaxCategory/cbc:TierRange"))
        assertEquals(BigDecimal("6.00"), xml.decimal("$isc/cbc:TaxAmount"))          // 60.00 x 10%
        val igv = "/inv:Invoice/cac:InvoiceLine[2]/cac:TaxTotal/cac:TaxSubtotal[cac:TaxCategory/cac:TaxScheme/cbc:ID='1000']"
        assertEquals(BigDecimal("66.00"), xml.decimal("$igv/cbc:TaxableAmount"))     // SUPUESTO REG-053
        assertEquals(BigDecimal("11.88"), xml.decimal("$igv/cbc:TaxAmount"))
        // Cabecera: 1000 + 60 + 6 + 180 + 11.88 = 1257.88 (igual al ejemplo de samples/factura-01.json)
        assertEquals(BigDecimal("1257.88"), xml.decimal("/inv:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"))
        assertEquals(BigDecimal("197.88"), xml.decimal("/inv:Invoice/cac:TaxTotal/cbc:TaxAmount"))
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @ParameterizedTest(name = "sistema {0}")
    @EnumSource(SistemaIsc::class)
    fun `los tres sistemas del catalogo 08 generan XML valido con su TierRange (MT-065)`(sistema: SistemaIsc) {
        val isc = when (sistema) {
            SistemaIsc.AL_VALOR -> Isc(sistema, BigDecimal("10.00"))
            SistemaIsc.MONTO_FIJO -> Isc(sistema, BigDecimal("0.25"))
            SistemaIsc.PRECIO_VENTA_PUBLICO -> Isc(sistema, BigDecimal("5.00"), precioVentaPublico = BigDecimal("3.50"))
        }
        val gen = casoDeUso().ejecutar(factura(bebida.copy(isc = isc)))
        val xml = XmlUbl(gen.xml)
        assertEquals(sistema.codigo, xml.texto("$subtotales/cac:TaxCategory/cbc:TierRange"))
        val esperado = when (sistema) {
            SistemaIsc.AL_VALOR -> "6.00"             // 60.00 x 10%
            SistemaIsc.MONTO_FIJO -> "6.00"           // 24 x 0.25
            SistemaIsc.PRECIO_VENTA_PUBLICO -> "4.20" // 24 x 3.50 x 5%
        }
        assertEquals(BigDecimal(esperado), xml.decimal("$subtotales[cac:TaxCategory/cac:TaxScheme/cbc:ID='2000']/cbc:TaxAmount"))
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @Test
    fun `ICBPER con bolsas en BaseUnitMeasure NIU y monto unitario en TaxCategory PerUnitAmount (MT-190 a MT-192, REG-054)`() {
        val gen = casoDeUso().ejecutar(factura(arroz.copy(bolsasPlastico = 3)))
        val xml = XmlUbl(gen.xml)
        val icbper = "$subtotales[cac:TaxCategory/cac:TaxScheme/cbc:ID='7152']"
        assertEquals(BigDecimal("3"), xml.decimal("$icbper/cbc:BaseUnitMeasure"))
        assertEquals("NIU", xml.texto("$icbper/cbc:BaseUnitMeasure/@unitCode"))
        assertEquals(BigDecimal("0.50"), xml.decimal("$icbper/cac:TaxCategory/cbc:PerUnitAmount"))
        assertEquals(BigDecimal("1.50"), xml.decimal("$icbper/cbc:TaxAmount"))
        assertEquals(BigDecimal("1181.50"), xml.decimal("/inv:Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount"))
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @Test
    fun `sin tasa de IGV configurada no se genera nada - ninguna tasa esta fija en el codigo (RNF-06, REG-050)`() {
        val e = assertFailsWith<ParametroNoConfiguradoException> { casoDeUso(Fixtures.parametrosSinConfigurar).ejecutar(factura()) }
        assertEquals(true, e.message!!.contains("REG-050"))
    }
}
