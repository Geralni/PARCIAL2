// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de producto/movimiento-almacen .schema.yaml
package pe.abc.fe.inventario

import pe.abc.fe.comun.*

enum class TipoProducto { BIEN, SERVICIO } // interno

data class ProductoDto(
    val id: String?,                            // interno
    val codigoInterno: String,                  // MT-070
    val nombre: String,                         // MT-069
    val tipo: TipoProducto,                     // interno
    val codigoProductoSunat: String?,           // MT-071  TODO(spec: REG-027)
    val unidadMedida: CodigoCatalogo,           // MT-050 (cat. 03)
    val afectacionIgvDefecto: CodigoCatalogo?,  // MT-064 (cat. 07)
    val sistemaIsc: CodigoCatalogo?,            // MT-065 (cat. 08)  TODO(spec: REG-052)
    val sujetoIcbper: Boolean,                  // MT-190
    val valorUnitarioVenta: PrecioUnitario?,    // MT-072
    val codigoExistencia: String?,              // interno (12.1, PENDIENTE)
    val requiereHomologacion: Boolean,          // interno  TODO(spec: REG-132)
    val origen: Origen?,                        // interno
)

enum class TipoMovimiento { INGRESO, SALIDA } // interno

data class MovimientoAlmacenDto(
    val id: String?,                              // interno
    val fecha: Fecha,                             // interno  TODO(spec: REG-130)
    val tipo: TipoMovimiento,                     // interno  TODO(spec: REG-131)
    val productoCodigo: String,                   // MT-070
    val cantidad: Cantidad,                       // MT-049  TODO(spec: REG-135)
    val unidadMedida: CodigoCatalogo?,            // MT-050
    val establecimientoCodigo: CodigoEstablecimiento, // MT-076
    val comprobante: ReferenciaDocumento?,        // interno
    val documentoInternoLegado: String?,          // MT-018 (nro_documento)
    val tipoOperacion12_1: String?,               // interno (PENDIENTE)
    val origen: Origen,                           // interno  TODO(spec: REG-134)
)
