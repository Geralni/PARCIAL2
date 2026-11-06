// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de schemas/common.schema.yaml y schemas/catalogos.schema.yaml.
package pe.abc.fe.comun

/** n(12,2). REG-067. */
@JvmInline value class Monto(val valor: String)            // TODO(spec: REG-067) formato n(12,2)

/** n(15,2) para anticipos. REG-067. */
@JvmInline value class MontoAnticipo(val valor: String)    // TODO(spec: REG-067)

/** n(12,10). REG-067, REG-135. */
@JvmInline value class Cantidad(val valor: String)         // TODO(spec: REG-067)

/** n(12,10). REG-067. */
@JvmInline value class PrecioUnitario(val valor: String)   // TODO(spec: REG-067)

/** n(3,5). REG-067. */
@JvmInline value class Porcentaje(val valor: String)       // TODO(spec: REG-067)

/** yyyy-mm-dd. */
@JvmInline value class Fecha(val iso: String)              // TODO(spec: REG-080)

/** hh:mm:ss (DISC-16). */
@JvmInline value class Hora(val iso: String)               // TODO(spec: REG-082)

/** AAAAMM. */
@JvmInline value class Periodo(val valor: String)

/** 11 dígitos con dígito verificador. */
@JvmInline value class Ruc(val valor: String)              // TODO(spec: REG-040) TODO(spec: REG-041)

/** F### | B### | NNNN (contingencia). */
@JvmInline value class SerieCodigo(val valor: String)      // TODO(spec: REG-030) TODO(spec: REG-031) TODO(spec: REG-033)

/** 1..99999999. */
@JvmInline value class Correlativo(val valor: Long)        // TODO(spec: REG-035)

/** AddressTypeCode n4. */
@JvmInline value class CodigoEstablecimiento(val valor: String) // TODO(spec: REG-036)

/**
 * Código de un catálogo SUNAT. Los valores válidos NO se duplican aquí: se cargan de
 * catalogs/catNN.json mediante CatalogoRepositoryPort (fuente no oficial, RSK-02).
 */
data class CodigoCatalogo(
    val catalogo: String, // "01".."53"  interno
    val codigo: String,   // interno (la fila MT la da el campo que lo usa)  TODO(spec: REG-010) .. REG-027: pertenece al catálogo
)

data class Direccion(
    val ubigeo: String?,        // MT-077 (Catálogo 13, n6)  TODO(spec: REG-038)
    val departamento: String?,  // interno
    val provincia: String?,     // interno
    val distrito: String?,      // interno
    val linea: String?,         // interno
)

data class ReferenciaDocumento(
    val tipo: CodigoCatalogo,     // MT-100 (cat. 01)
    val serie: SerieCodigo,       // MT-099
    val correlativo: Correlativo, // MT-099
)

data class CargoDescuento(
    val esCargo: Boolean,         // MT-029 / MT-054   TODO(spec: REG-024)
    val codigo: CodigoCatalogo,   // MT-030 / MT-055 (cat. 53)
    val factor: Porcentaje?,      // MT-031 / MT-056
    val monto: Monto,             // MT-032 / MT-057
    val base: Monto?,             // MT-033 / MT-058
)

enum class FuenteOrigen { SISTEMA, LEGADO, CONTINGENCIA, DISPOSITIVO_OFFLINE }

/** Trazabilidad de procedencia (R-01). Inmutable. REG-134. */
data class Origen(
    val fuente: FuenteOrigen,        // interno
    val loteImportacion: String?,    // interno
    val archivo: String?,            // interno
    val fila: Int?,                  // interno
    val hashFila: String?,           // interno
    val dispositivoId: String?,      // interno
)
