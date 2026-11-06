package pe.abc.fe.aplicacion

import pe.abc.fe.dominio.CalculadoraComprobante
import pe.abc.fe.dominio.Comprobante
import pe.abc.fe.dominio.ComprobanteCalculado
import pe.abc.fe.dominio.ComprobanteInvalidoException
import pe.abc.fe.dominio.ValidadorComprobante
import pe.abc.fe.dominio.Violacion

data class XmlGenerado(val nombreArchivo: String, val xml: String, val calculado: ComprobanteCalculado)

/**
 * Caso de uso (puerto de entrada) del 2.º parcial: comprobante del dominio -> XML UBL 2.1 Invoice válido.
 * Pipeline (ADR-007, REG-094): reglas de negocio -> cálculo -> XML (clases del XSD) -> validación XSD.
 * La firma (REG-090) y el envío al OSE quedan fuera de este parcial.
 */
class GenerarXmlComprobanteUseCase(
    parametros: ParametrosTributariosPort,
    private val generador: GeneradorUblPort,
    private val validadorXsd: ValidadorXsdPort,
) {
    private val calculadora = CalculadoraComprobante(parametros)

    fun ejecutar(comprobante: Comprobante, rucEmisor: String = comprobante.emisor.ruc): XmlGenerado {
        val violaciones = ValidadorComprobante.violaciones(comprobante)
        if (violaciones.isNotEmpty()) throw ComprobanteInvalidoException(violaciones)

        val calculado = calculadora.calcular(comprobante)
        val deCuotas = ValidadorComprobante.violacionesDeCuotas(comprobante, calculado.totales.importeTotal)
        if (deCuotas.isNotEmpty()) throw ComprobanteInvalidoException(deCuotas)

        val xml = generador.generar(calculado)
        val erroresXsd = validadorXsd.validar(xml)
        if (erroresXsd.isNotEmpty()) {
            throw ComprobanteInvalidoException(erroresXsd.map { Violacion("REG-094", "xml", it) })
        }
        // Nombre de archivo SUNAT: RUC-TIPO-SERIE-NUMERO.xml
        val nombre = "$rucEmisor-${comprobante.tipo.codigo}-${comprobante.serie}-${comprobante.correlativo}.xml"
        return XmlGenerado(nombre, xml, calculado)
    }
}
