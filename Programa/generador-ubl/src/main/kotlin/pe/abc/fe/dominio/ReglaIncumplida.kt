package pe.abc.fe.dominio

/** Una regla de specs/02-dominio-y-contratos/reglas-de-validacion.md que no se cumple. */
data class Violacion(val regla: String, val campo: String, val mensaje: String) {
    override fun toString() = "$regla [$campo]: $mensaje"
}

/** El comprobante incumple una o más reglas: no se genera XML (equivale al Problema VALIDACION / 422). */
class ComprobanteInvalidoException(val violaciones: List<Violacion>) :
    RuntimeException("Comprobante inválido:\n" + violaciones.joinToString("\n") { " - $it" })

/** Falta un parámetro tributario con vigencia (RNF-06): no se fija ninguna tasa en el código. */
class ParametroNoConfiguradoException(regla: String, parametro: String) :
    RuntimeException("$regla: el parámetro tributario '$parametro' no está configurado para la fecha de emisión")
