// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de emisor/establecimiento/firma-digital/parametro-tributario .schema.yaml
package pe.abc.fe.emision

import pe.abc.fe.comun.*

enum class CanalEnvio { OSE, SUNAT } // interno (ADR-004)

data class EstablecimientoDto(
    val codigoSunat: CodigoEstablecimiento, // MT-076  TODO(spec: REG-036)
    val codigoInterno: String?,             // interno
    val descripcion: String,                // interno
    val direccion: Direccion?,              // interno
    val permiteOffline: Boolean,            // interno (ADR-006)
)

data class EmisorDto(
    val ruc: Ruc,                                   // MT-073  TODO(spec: REG-040) TODO(spec: REG-041)
    val razonSocial: String,                        // MT-075
    val nombreComercial: String?,                   // MT-021
    val domicilioFiscal: Direccion,                 // interno
    val establecimientos: List<EstablecimientoDto>, // MT-076
    /** Alias en el almacén seguro del SO. NUNCA la clave ni la contraseña. */
    val certificadoAlias: String?,                  // interno  TODO(spec: REG-093)
    val canalEnvio: CanalEnvio,                     // interno
)

enum class FirmadoPor { LOCAL_WINDOWS, LOCAL_ANDROID, PROVEEDOR_OSE } // interno

/** Metadatos de la firma aplicada. Sin secretos (REG-093). */
data class FirmaDigitalDto(
    val firmanteRuc: Ruc,                  // MT-020  TODO(spec: REG-092)
    val certificadoHuella: String,         // MT-001  TODO(spec: REG-091)
    val certificadoVigenteDesde: Fecha?,   // interno
    val certificadoVigenteHasta: Fecha?,   // interno
    val algoritmo: String?,                // MT-001 (PENDIENTE de norma)
    val digestValue: String?,              // MT-001
    val fechaFirma: String,                // interno (ISO date-time)
    val firmadoPor: FirmadoPor?,           // interno
)

enum class EstadoVerificacion { VERIFICADO, PENDIENTE } // interno

/** RNF-06: ninguna tasa en código. */
data class ParametroTributarioDto(
    val codigo: String,                    // interno (IGV_TASA, ISC_TASA, ICBPER_MONTO_UNITARIO, ...)
    val tributo: CodigoCatalogo?,          // MT-066 (cat. 05)
    val productoCodigo: String?,           // interno
    val valor: String?,                    // MT-063 (null mientras esté PENDIENTE)
    val vigenteDesde: Fecha,               // interno
    val vigenteHasta: Fecha?,              // interno
    val fuenteNormativa: String?,          // interno
    val estadoVerificacion: EstadoVerificacion, // interno
)
