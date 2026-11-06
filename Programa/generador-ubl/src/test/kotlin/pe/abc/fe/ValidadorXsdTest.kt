package pe.abc.fe

import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import pe.abc.fe.Fixtures.casoDeUso
import pe.abc.fe.Fixtures.factura
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** El validador XSD (REG-094) debe detectar XML inválidos, no solo aceptar los buenos. */
@DisplayName("Validador XSD UBL 2.1 (REG-094)")
class ValidadorXsdTest {

    private val xmlValido = casoDeUso().ejecutar(factura()).xml

    @Test
    fun `acepta el XML generado`() {
        assertEquals(emptyList(), Fixtures.validadorXsd.validar(xmlValido))
    }

    @Test
    fun `rechaza un elemento que no existe en el XSD`() {
        val malo = xmlValido.replace("<cbc:IssueDate>", "<cbc:Inventado>X</cbc:Inventado><cbc:IssueDate>")
        assertTrue(Fixtures.validadorXsd.validar(malo).isNotEmpty())
    }

    @Test
    fun `rechaza elementos fuera del orden del XSD`() {
        val id = Regex("<cbc:ID>F001-1</cbc:ID>\\s*").find(xmlValido)!!.value
        val malo = xmlValido.replaceFirst(id, "").replace("</cbc:IssueDate>", "</cbc:IssueDate>$id")
        assertTrue(Fixtures.validadorXsd.validar(malo).isNotEmpty())
    }

    @Test
    fun `rechaza la falta de un elemento obligatorio (LegalMonetaryTotal 1_1)`() {
        val malo = xmlValido.replace(Regex("<cac:LegalMonetaryTotal>.*?</cac:LegalMonetaryTotal>", RegexOption.DOT_MATCHES_ALL), "")
        assertTrue(Fixtures.validadorXsd.validar(malo).isNotEmpty())
    }

    @Test
    fun `rechaza XML mal formado`() {
        assertTrue(Fixtures.validadorXsd.validar("<Invoice>").isNotEmpty())
    }
}
