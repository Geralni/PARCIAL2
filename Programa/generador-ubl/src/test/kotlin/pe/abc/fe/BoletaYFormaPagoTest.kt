package pe.abc.fe

import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import pe.abc.fe.Fixtures.boleta
import pe.abc.fe.Fixtures.casoDeUso
import pe.abc.fe.Fixtures.factura
import pe.abc.fe.dominio.ComprobanteInvalidoException
import pe.abc.fe.dominio.Cuota
import pe.abc.fe.dominio.FormaPago
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

@DisplayName("Boleta 03 y forma de pago (contado / crédito con cuotas)")
class BoletaYFormaPagoTest {

    @Test
    fun `boleta 03 con serie B y adquirente con DNI genera XML valido (MT-082, REG-031, DISC-04, DISC-13)`() {
        val gen = casoDeUso().ejecutar(boleta())
        val xml = XmlUbl(gen.xml)
        assertEquals("03", xml.texto("/inv:Invoice/cbc:InvoiceTypeCode"))
        assertEquals("B001-1", xml.texto("/inv:Invoice/cbc:ID"))
        assertEquals("1", xml.texto("/inv:Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID/@schemeID"))
        assertEquals("20000000001-03-B001-1.xml", gen.nombreArchivo)
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @Test
    fun `contado - PaymentTerms FormaPago con Contado (MT-193, REG-028)`() {
        val xml = XmlUbl(casoDeUso().ejecutar(factura()).xml)
        assertEquals("FormaPago", xml.texto("/inv:Invoice/cac:PaymentTerms/cbc:ID"))
        assertEquals("Contado", xml.texto("/inv:Invoice/cac:PaymentTerms/cbc:PaymentMeansID"))
        assertEquals(1, xml.cantidad("/inv:Invoice/cac:PaymentTerms"))
    }

    @Test
    fun `credito - monto pendiente y cuotas Cuota001 y Cuota002 con fecha (MT-193 a MT-196, REG-028, REG-029)`() {
        val credito = FormaPago.Credito(listOf(
            Cuota(BigDecimal("590.00"), LocalDate.of(2026, 11, 26)),
            Cuota(BigDecimal("590.00"), LocalDate.of(2026, 12, 26)),
        ))
        val gen = casoDeUso().ejecutar(factura().copy(formaPago = credito, fechaVencimiento = LocalDate.of(2026, 12, 26)))
        val xml = XmlUbl(gen.xml)
        val pt = "/inv:Invoice/cac:PaymentTerms"
        assertEquals(3, xml.cantidad(pt))
        assertEquals(BigDecimal("1180.00"), xml.decimal("$pt[cbc:PaymentMeansID='Credito']/cbc:Amount"))
        assertEquals(BigDecimal("590.00"), xml.decimal("$pt[cbc:PaymentMeansID='Cuota001']/cbc:Amount"))
        assertEquals("2026-12-26", xml.texto("$pt[cbc:PaymentMeansID='Cuota002']/cbc:PaymentDueDate"))
        assertEquals("2026-12-26", xml.texto("/inv:Invoice/cbc:DueDate"))
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(gen.xml))
    }

    @Test
    fun `credito - si las cuotas no suman el total, no se genera (REG-029)`() {
        val credito = FormaPago.Credito(listOf(Cuota(BigDecimal("100.00"), LocalDate.of(2026, 11, 26))))
        val e = assertFailsWith<ComprobanteInvalidoException> { casoDeUso().ejecutar(factura().copy(formaPago = credito)) }
        assertTrue(e.violaciones.any { it.regla == "REG-029" })
    }
}
