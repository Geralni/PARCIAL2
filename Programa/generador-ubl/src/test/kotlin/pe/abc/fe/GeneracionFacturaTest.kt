package pe.abc.fe

import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import pe.abc.fe.Fixtures.casoDeUso
import pe.abc.fe.Fixtures.factura
import java.math.BigDecimal
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** Generación de la factura (01): estructura, cabecera, partes y totales. Cada test cita su fila MT o regla REG. */
@DisplayName("Factura 01: generación del XML UBL 2.1")
class GeneracionFacturaTest {

    private val generado = casoDeUso().ejecutar(factura())
    private val xml = XmlUbl(generado.xml)

    @Test
    fun `el XML generado es valido contra UBL-Invoice-2_1 xsd (REG-094)`() {
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(generado.xml))
    }

    @Test
    fun `nombre de archivo RUC-TIPO-SERIE-NUMERO`() {
        assertEquals("20000000001-01-F001-1.xml", generado.nombreArchivo)
    }

    @Test
    fun `versiones UBL 2_1 y personalizacion 2_0 (MT-002, MT-003, REG-001, REG-002)`() {
        assertEquals("2.1", xml.texto("/inv:Invoice/cbc:UBLVersionID"))
        assertEquals("2.0", xml.texto("/inv:Invoice/cbc:CustomizationID"))
    }

    @Test
    fun `serie-numero, fecha y hora de emision (MT-006, MT-007, MT-008)`() {
        assertEquals("F001-1", xml.texto("/inv:Invoice/cbc:ID"))
        assertEquals("2026-10-27", xml.texto("/inv:Invoice/cbc:IssueDate"))
        assertEquals("10:15:00", xml.texto("/inv:Invoice/cbc:IssueTime"))
    }

    @Test
    fun `tipo de documento 01 y tipo de operacion en listID con catalogo 51 (MT-010, MT-087)`() {
        assertEquals("01", xml.texto("/inv:Invoice/cbc:InvoiceTypeCode"))
        assertEquals("0101", xml.texto("/inv:Invoice/cbc:InvoiceTypeCode/@listID"))
        assertEquals("urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01", xml.texto("/inv:Invoice/cbc:InvoiceTypeCode/@listURI"))
        assertEquals("urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo51", xml.texto("/inv:Invoice/cbc:InvoiceTypeCode/@listSchemeURI"))
        assertEquals(0, xml.cantidad("/inv:Invoice/cbc:ProfileID"), "ProfileID ya no se usa (DISC-01)")
    }

    @Test
    fun `moneda y leyenda con codigos de catalogo (MT-011, MT-012, MT-013)`() {
        assertEquals("PEN", xml.texto("/inv:Invoice/cbc:DocumentCurrencyCode"))
        assertEquals("ISO 4217 Alpha", xml.texto("/inv:Invoice/cbc:DocumentCurrencyCode/@listID"))
        assertEquals("1000", xml.texto("/inv:Invoice/cbc:Note/@languageLocaleID"))
    }

    @Test
    fun `emisor en PartyIdentification y PartyLegalEntity, estructura vigente (MT-073 a MT-077, DISC-25)`() {
        val p = "/inv:Invoice/cac:AccountingSupplierParty/cac:Party"
        assertEquals("20000000001", xml.texto("$p/cac:PartyIdentification/cbc:ID"))
        assertEquals("6", xml.texto("$p/cac:PartyIdentification/cbc:ID/@schemeID"))
        assertEquals("ABC SOFTWARE CORP S.A.C. (FICTICIO)", xml.texto("$p/cac:PartyLegalEntity/cbc:RegistrationName"))
        assertEquals("0000", xml.texto("$p/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:AddressTypeCode"))
        assertEquals("150101", xml.texto("$p/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID"))
        assertEquals(0, xml.cantidad("$p/cac:PartyTaxScheme"), "La estructura de 2017 (PartyTaxScheme) no se usa")
    }

    @Test
    fun `adquirente con RUC (MT-078, MT-079, MT-088)`() {
        val p = "/inv:Invoice/cac:AccountingCustomerParty/cac:Party"
        assertEquals("20000000002", xml.texto("$p/cac:PartyIdentification/cbc:ID"))
        assertEquals("6", xml.texto("$p/cac:PartyIdentification/cbc:ID/@schemeID"))
        assertEquals("BODEGA FICTICIA LOS ANDES S.A.C.", xml.texto("$p/cac:PartyLegalEntity/cbc:RegistrationName"))
    }

    @Test
    fun `totales coherentes con las lineas (MT-034, MT-041, MT-042, MT-046, REG-057, REG-061, REG-066)`() {
        // 10 x 100.00 = 1000.00 ; IGV 18.00% (tasa de prueba) = 180.00 ; total 1180.00
        val t = "/inv:Invoice/cac:LegalMonetaryTotal"
        assertEquals(BigDecimal("1000.00"), xml.decimal("$t/cbc:LineExtensionAmount"))
        assertEquals(BigDecimal("1180.00"), xml.decimal("$t/cbc:TaxInclusiveAmount"))
        assertEquals(BigDecimal("1180.00"), xml.decimal("$t/cbc:PayableAmount"))
        assertEquals(BigDecimal("180.00"), xml.decimal("/inv:Invoice/cac:TaxTotal/cbc:TaxAmount"))
        assertEquals("1000", xml.texto("/inv:Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID"))
    }

    @Test
    fun `una sola moneda en todos los currencyID (REG-069)`() {
        assertEquals(0, xml.cantidad("//@currencyID[. != 'PEN']"))
        assertTrue(xml.cantidad("//@currencyID") > 5)
    }

    @Test
    fun `linea con unidad del catalogo 03, precio con IGV y producto SUNAT (MT-048 a MT-053, MT-069 a MT-072)`() {
        val l = "/inv:Invoice/cac:InvoiceLine[1]"
        assertEquals("1", xml.texto("$l/cbc:ID"))
        assertEquals("BG", xml.texto("$l/cbc:InvoicedQuantity/@unitCode"))
        assertEquals(BigDecimal("10"), xml.decimal("$l/cbc:InvoicedQuantity"))
        assertEquals(BigDecimal("1000.00"), xml.decimal("$l/cbc:LineExtensionAmount"))
        assertEquals(BigDecimal("118.00"), xml.decimal("$l/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount"))
        assertEquals("01", xml.texto("$l/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode"))
        assertEquals("ARROZ SUPERIOR SACO 50 KG", xml.texto("$l/cac:Item/cbc:Description"))
        assertEquals("ARR-050", xml.texto("$l/cac:Item/cac:SellersItemIdentification/cbc:ID"))
        assertEquals("50221101", xml.texto("$l/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode"))
        assertEquals(BigDecimal("100.00"), xml.decimal("$l/cac:Price/cbc:PriceAmount"))
    }

    @Test
    fun `prefijos UBL legibles (cac, cbc) en lugar de ns1, ns2`() {
        assertTrue(generado.xml.contains("<cbc:UBLVersionID>"))
        assertTrue(generado.xml.contains("<cac:InvoiceLine>"))
        assertTrue(!generado.xml.contains("ns1:"))
    }
}
