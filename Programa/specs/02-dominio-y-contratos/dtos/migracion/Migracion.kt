// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de ficha-legado/importacion-legado .schema.yaml
package pe.abc.fe.migracion

/** Fila del legado SIN limpiar: todo es texto. */
@Suppress("PropertyName")
data class FichaLegadoDto(
    val fecha: String,          // interno  TODO(spec: REG-130)
    val ingreso: String,        // interno  TODO(spec: REG-131) TODO(spec: REG-135)
    val salida: String,         // interno  TODO(spec: REG-131) TODO(spec: REG-135)
    val producto: String,       // interno  TODO(spec: REG-132)
    val nro_documento: String,  // interno  TODO(spec: REG-133)
)

enum class ModoImportacion { SIMULACION, DEFINITIVO } // interno
enum class EstadoImportacion { RECIBIDO, VALIDANDO, EN_CUARENTENA_PARCIAL, COMPLETADO, FALLIDO } // interno

data class TotalesImportacionDto(
    val filasLeidas: Int,             // interno
    val movimientosCreados: Int,      // interno
    val productosProvisionales: Int,  // interno
    val filasEnCuarentena: Int,       // interno
    val advertencias: Int,            // interno
)

data class IncidenciaDto(
    val fila: Int,          // interno
    val regla: String,      // interno (REG-13x)
    val severidad: String,  // interno
    val mensaje: String?,   // interno
)

data class ImportacionLegadoDto(
    val id: String,                     // interno
    val archivo: String?,               // interno
    val hashArchivo: String?,           // interno  TODO(spec: REG-160)
    val modo: ModoImportacion?,         // interno
    val estado: EstadoImportacion,      // interno
    val totales: TotalesImportacionDto?,// interno
    val incidencias: List<IncidenciaDto>, // interno
)
