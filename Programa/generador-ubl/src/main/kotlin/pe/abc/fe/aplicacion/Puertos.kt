package pe.abc.fe.aplicacion

import pe.abc.fe.dominio.ComprobanteCalculado
import pe.abc.fe.dominio.ParametrosTributarios

/** Puerto de salida: tasas y montos con vigencia (RNF-06). Extiende la interfaz que necesita el dominio. */
interface ParametrosTributariosPort : ParametrosTributarios

/** Puerto de salida: dominio -> XML UBL (ADR-007: clases generadas desde el XSD). */
interface GeneradorUblPort {
    fun generar(comprobante: ComprobanteCalculado): String
}

/** Puerto de salida: validación contra el XSD ANTES de firmar (REG-094). Lista vacía = válido. */
interface ValidadorXsdPort {
    fun validar(xml: String): List<String>
}
