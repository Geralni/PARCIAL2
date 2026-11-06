package pe.abc.fe

import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import pe.abc.fe.Fixtures.arroz
import pe.abc.fe.Fixtures.casoDeUso
import pe.abc.fe.Fixtures.factura
import pe.abc.fe.dominio.Adquirente
import pe.abc.fe.dominio.Comprobante
import pe.abc.fe.dominio.ComprobanteInvalidoException
import pe.abc.fe.dominio.Leyenda
import java.math.BigDecimal
import java.time.LocalDate
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

/** Reglas que el XSD NO valida (mapa-xsd.md §3): si se incumplen, no se genera XML. */
@DisplayName("Validaciones de negocio antes de generar el XML")
class ValidacionesTest {

    private fun reglasIncumplidas(c: Comprobante): Set<String> =
        assertFailsWith<ComprobanteInvalidoException> { casoDeUso().ejecutar(c) }.violaciones.map { it.regla }.toSet()

    @Test
    fun `factura con serie de boleta (REG-030)`() {
        assertTrue("REG-030" in reglasIncumplidas(factura().copy(serie = "B001")))
    }

    @Test
    fun `serie de contingencia numerica es valida (REG-033)`() {
        val gen = casoDeUso().ejecutar(factura().copy(serie = "0001"))
        assertEquals("0001-1", XmlUbl(gen.xml).texto("/inv:Invoice/cbc:ID"))
    }

    @Test
    fun `correlativo fuera de rango (REG-035)`() {
        assertTrue("REG-035" in reglasIncumplidas(factura().copy(correlativo = 0)))
        assertTrue("REG-035" in reglasIncumplidas(factura().copy(correlativo = 100_000_000)))
    }

    @Test
    fun `RUC del emisor con longitud invalida (REG-040)`() {
        assertTrue("REG-040" in reglasIncumplidas(factura().copy(emisor = Fixtures.emisor.copy(ruc = "2000000000"))))
    }

    @Test
    fun `adquirente con tipo 6 y numero que no es RUC (REG-042)`() {
        assertTrue("REG-042" in reglasIncumplidas(factura().copy(adquirente = Adquirente("6", "123", "X"))))
    }

    @Test
    fun `factura a un adquirente con DNI (REG-044)`() {
        assertTrue("REG-044" in reglasIncumplidas(factura().copy(adquirente = Fixtures.clienteDni)))
    }

    @Test
    fun `tipo de documento de identidad fuera del catalogo 06 (REG-015)`() {
        assertTrue("REG-015" in reglasIncumplidas(factura().copy(adquirente = Adquirente("Z", "20000000002", "X"))))
    }

    @Test
    fun `unidad de medida que no esta en el catalogo 03 no es texto libre (REG-012)`() {
        assertTrue("REG-012" in reglasIncumplidas(factura(arroz.copy(unidadMedida = "SACOS"))))
    }

    @Test
    fun `moneda fuera del catalogo 02 (REG-011)`() {
        assertTrue("REG-011" in reglasIncumplidas(factura().copy(moneda = "ZZZ")))
    }

    @Test
    fun `tipo de operacion fuera del catalogo 51 (REG-021)`() {
        assertTrue("REG-021" in reglasIncumplidas(factura().copy(tipoOperacion = "9999")))
    }

    @Test
    fun `leyenda fuera del catalogo 52 (REG-025)`() {
        assertTrue("REG-025" in reglasIncumplidas(factura().copy(leyendas = listOf(Leyenda("0000", "X")))))
    }

    @Test
    fun `sin lineas no hay comprobante (REG-006)`() {
        assertTrue("REG-006" in reglasIncumplidas(factura().copy(lineas = emptyList())))
    }

    @Test
    fun `cantidad cero (REG-067)`() {
        assertTrue("REG-067" in reglasIncumplidas(factura(arroz.copy(cantidad = BigDecimal.ZERO))))
    }

    @Test
    fun `vencimiento anterior a la emision (REG-081)`() {
        assertTrue("REG-081" in reglasIncumplidas(factura().copy(fechaVencimiento = LocalDate.of(2026, 1, 1))))
    }

    @Test
    fun `codigo de producto SUNAT que no tiene 8 digitos (REG-027)`() {
        assertTrue("REG-027" in reglasIncumplidas(factura(arroz.copy(codigoProductoSunat = "123"))))
    }

    @Test
    fun `se informan todas las violaciones juntas, no solo la primera`() {
        val c = factura().copy(serie = "X1", moneda = "ZZZ", emisor = Fixtures.emisor.copy(ruc = "1"))
        assertTrue(reglasIncumplidas(c).containsAll(setOf("REG-030", "REG-011", "REG-040")))
    }
}
