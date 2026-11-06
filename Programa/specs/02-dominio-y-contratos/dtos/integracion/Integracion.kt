// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de respuesta-sunat/comunicacion-baja/resumen-diario/validacion-ruc/problema .schema.yaml
package pe.abc.fe.integracion

import pe.abc.fe.comun.*
import pe.abc.fe.emision.CanalEnvio
import pe.abc.fe.emision.FirmaDigitalDto
import pe.abc.fe.emision.TributoDto

enum class ResultadoSunat { ACEPTADO, ACEPTADO_CON_OBSERVACIONES, RECHAZADO, EN_PROCESO, ERROR_COMUNICACION } // interno

data class RespuestaSunatDto(
    val canal: CanalEnvio,             // interno
    val ticket: String?,               // interno
    val resultado: ResultadoSunat,     // interno (SUP-06)
    val codigoRespuesta: String?,      // interno (códigos oficiales PENDIENTE)
    val descripcion: String?,          // interno
    val observaciones: List<String>,   // interno
    val fechaRecepcion: String,        // interno
    val cdrHash: String?,              // interno
)

enum class EstadoProcesoAsincrono { PENDIENTE_ENVIO, EN_PROCESO, ACEPTADA, RECHAZADA } // interno

data class ItemBajaDto(
    val linea: Int?,                    // MT-179  TODO(spec: REG-121)
    val tipoComprobante: CodigoCatalogo,// MT-180 (cat. 01)
    val serie: String,                  // MT-181  TODO(spec: REG-124)
    val correlativo: Correlativo,       // MT-182
    val motivo: String,                 // MT-183
)

data class ComunicacionBajaDto(
    val id: String?,                    // interno
    val identificador: String?,         // MT-172 RA-<Fecha>-#####  TODO(spec: REG-121)
    val fechaGeneracion: Fecha?,        // MT-173  TODO(spec: REG-122)
    val fechaReferencia: Fecha,         // MT-174  TODO(spec: REG-111)
    val items: List<ItemBajaDto>,       // MT-179
    val estado: EstadoProcesoAsincrono?,// interno
    val ticket: String?,                // interno
    val firma: FirmaDigitalDto?,        // MT-175
    val respuestaSunat: RespuestaSunatDto?, // interno
)

data class TotalPorTipoDto(
    val codigo: String,                 // MT-159 (cat. 11, PENDIENTE; DISC-09)
    val monto: Monto,                   // MT-158
)

data class AdquirenteResumenDto(
    val tipoDocumento: CodigoCatalogo?, // MT-153
    val numeroDocumento: String?,       // MT-152
)

data class ItemResumenDto(
    val linea: Int?,                            // MT-149
    val tipoComprobante: CodigoCatalogo,        // MT-151
    val serieNumero: String,                    // MT-150  TODO(spec: REG-120)
    val adquirente: AdquirenteResumenDto?,      // MT-152
    val documentoModificado: ReferenciaDocumento?, // MT-154
    val estadoItem: String,                     // MT-156 (cat. 19, PENDIENTE)  TODO(spec: REG-123)
    val moneda: CodigoCatalogo,                 // MT-157
    val importeTotal: Monto,                    // MT-157
    val totalesPorTipo: List<TotalPorTipoDto>,  // MT-158  TODO(spec: REG-124)
    val otrosCargos: Monto?,                    // MT-160
    val tributos: List<TributoDto>,             // MT-161
)

data class ResumenDiarioDto(
    val id: String?,                    // interno
    val identificador: String?,         // MT-142 RC-<Fecha>-#####  TODO(spec: REG-120)
    val fechaGeneracion: Fecha?,        // MT-143
    val fechaReferencia: Fecha,         // MT-144  TODO(spec: REG-122)
    val items: List<ItemResumenDto>,    // MT-149
    val estado: String?,                // interno
    val ticket: String?,                // interno
    val firma: FirmaDigitalDto?,        // MT-145
    val respuestaSunat: RespuestaSunatDto?, // interno
)

data class ConsultaPadronDto(
    val razonSocial: String?,  // MT-088
    val estado: String?,       // interno
    val condicion: String?,    // interno
    val consultadoEn: String?, // interno
)

data class ValidacionRucDto(
    val tipoDocumento: CodigoCatalogo,    // MT-079
    val numero: String,                   // MT-078
    val formatoValido: Boolean,           // interno  TODO(spec: REG-040) TODO(spec: REG-042) TODO(spec: REG-043)
    val digitoVerificadorValido: Boolean?,// interno  TODO(spec: REG-041) PENDIENTE
    val consultaPadron: ConsultaPadronDto?, // interno  TODO(spec: REG-046)
    val incidencias: List<String>,        // interno
)

data class ViolacionDto(
    val regla: String,       // interno (REG-XXX)
    val campo: String?,      // interno
    val severidad: String,   // interno
    val mensaje: String,     // interno
)

/** RFC 9457. */
data class ProblemaDto(
    val type: String,        // interno
    val title: String,       // interno
    val status: Int,         // interno
    val detail: String?,     // interno
    val instance: String?,   // interno
    val codigo: String?,     // interno
    val violaciones: List<ViolacionDto>, // interno
)
