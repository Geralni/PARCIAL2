package pe.abc.fe.ubl

import org.xml.sax.ErrorHandler
import org.xml.sax.SAXParseException
import pe.abc.fe.aplicacion.ValidadorXsdPort
import java.io.StringReader
import javax.xml.XMLConstants
import javax.xml.transform.stream.StreamSource
import javax.xml.validation.Schema
import javax.xml.validation.SchemaFactory

/**
 * Adaptador ValidadorXsdPort (REG-094): valida el XML contra UBL-Invoice-2.1.xsd ANTES de firmar.
 * El Schema compilado se carga una sola vez (ADR-007 §5).
 */
class ValidadorXsdUbl(recursoXsd: String = "/xsd/ubl-2.1/maindoc/UBL-Invoice-2.1.xsd") : ValidadorXsdPort {

    private val schema: Schema = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI).run {
        // Solo se permiten esquemas locales (classpath o archivo), nunca descargas.
        setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "file,jar:file")
        setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "")
        newSchema(ValidadorXsdUbl::class.java.getResource(recursoXsd) ?: error("No se encontró el XSD $recursoXsd"))
    }

    override fun validar(xml: String): List<String> {
        val errores = mutableListOf<String>()
        val validador = schema.newValidator().apply {
            setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "")
            errorHandler = object : ErrorHandler {
                override fun warning(e: SAXParseException) = Unit
                override fun error(e: SAXParseException) { errores += "línea ${e.lineNumber}: ${e.message}" }
                override fun fatalError(e: SAXParseException) { errores += "línea ${e.lineNumber}: ${e.message}" }
            }
        }
        try {
            validador.validate(StreamSource(StringReader(xml)))
        } catch (e: SAXParseException) {
            if (errores.isEmpty()) errores += "línea ${e.lineNumber}: ${e.message}"
        }
        return errores
    }
}
