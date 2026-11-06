// ESQUELETO DE ESPECIFICACIÓN (Fase 1). Sin lógica de negocio.
// Espejo de registro-ventas-14-1 / registro-compras-8-1 / registro-inventario-12-1 .schema.yaml
// Fuente 14.1 y 8.1: estructura PLE de la plantilla comunitaria (referencias/formatos/). 12.1: Git/FORMATO_12_1.pdf.
// Comentario "PLE n" = número de campo de la estructura PLE.
package pe.abc.fe.registros

import pe.abc.fe.comun.*

/** Formato 14.1 (PLE campos 1-35). TODO(spec: REG-140) TODO(spec: REG-143) */
data class FilaVentas141Dto(
    val cuo: String,                              // interno  PLE 2
    val correlativoAsiento: String,               // interno  PLE 3
    val fechaEmision: Fecha?,                     // MT-007  PLE 4
    val fechaVencimiento: Fecha?,                 // MT-009  PLE 5
    val tipoComprobante: String,                  // MT-010  PLE 6 (Tabla 10)  TODO(spec: REG-147)
    val serie: String,                            // MT-006  PLE 7
    val numero: String,                           // MT-006  PLE 8
    val numeroFinalConsolidado: String?,          // interno  PLE 9
    val clienteTipoDocumento: String?,            // MT-079  PLE 10 (Tabla 2)  TODO(spec: REG-045)
    val clienteNumeroDocumento: String?,          // MT-078  PLE 11
    val clienteRazonSocial: String?,              // MT-088  PLE 12
    val valorExportacion: Monto?,                 // MT-035  PLE 13
    val baseImponibleGravada: Monto?,             // MT-035  PLE 14
    val descuentoBaseImponible: Monto?,           // MT-043  PLE 15
    val igvIpm: Monto?,                           // MT-036  PLE 16
    val descuentoIgvIpm: Monto?,                  // interno  PLE 17
    val exonerado: Monto?,                        // MT-035  PLE 18
    val inafecto: Monto?,                         // MT-035  PLE 19
    val isc: Monto?,                              // MT-036  PLE 20
    val baseImponibleIvap: Monto?,                // MT-035  PLE 21
    val ivap: Monto?,                             // MT-036  PLE 22
    val icbper: Monto?,                           // MT-190  PLE 23
    val otrosTributosCargos: Monto?,              // MT-044  PLE 24
    val importeTotal: Monto,                      // MT-046  PLE 25
    val moneda: String?,                          // MT-013  PLE 26 (Tabla 4)
    val tipoCambio: String?,                      // interno  PLE 27  TODO(spec: REG-145)
    val documentoModificadoFecha: Fecha?,         // interno  PLE 28  TODO(spec: REG-144)
    val documentoModificadoTipo: String?,         // MT-100  PLE 29
    val documentoModificadoSerie: String?,        // MT-099  PLE 30
    val documentoModificadoNumero: String?,       // MT-099  PLE 31
    val contratoProyecto: String?,                // interno  PLE 32
    val errorTipoCambio: String?,                 // interno  PLE 33
    val indicadorMediosPago: String?,             // interno  PLE 34
    val estadoAnotacion: String,                  // interno  PLE 35  TODO(spec: REG-146)
)

data class RegistroVentas141Dto(
    val periodo: Periodo,                 // interno  PLE 1
    val rucEmisor: Ruc,                   // MT-073
    val razonSocial: String?,             // MT-075
    val filas: List<FilaVentas141Dto>,    // interno
)

/** Formato 8.1 (PLE campos 1-42). Comprobantes RECIBIDOS: todo es interno frente al Anexo 9-A. TODO(spec: REG-141) */
data class FilaCompras81Dto(
    val cuo: String,                          // interno  PLE 2
    val correlativoAsiento: String,           // interno  PLE 3
    val fechaEmision: Fecha,                  // interno  PLE 4
    val fechaVencimientoPago: Fecha?,         // interno  PLE 5
    val tipoComprobante: String,              // interno  PLE 6
    val serie: String?,                       // interno  PLE 7
    val anioDua: String?,                     // interno  PLE 8
    val numero: String,                       // interno  PLE 9
    val numeroFinalConsolidado: String?,      // interno  PLE 10
    val proveedorTipoDocumento: String?,      // interno  PLE 11
    val proveedorNumeroDocumento: String?,    // interno  PLE 12
    val proveedorRazonSocial: String?,        // interno  PLE 13
    val baseGravadaDestinoGravado: Monto?,    // interno  PLE 14
    val igvDestinoGravado: Monto?,            // interno  PLE 15
    val baseGravadaDestinoMixto: Monto?,      // interno  PLE 16
    val igvDestinoMixto: Monto?,              // interno  PLE 17
    val baseGravadaSinCredito: Monto?,        // interno  PLE 18
    val igvSinCredito: Monto?,                // interno  PLE 19
    val adquisicionesNoGravadas: Monto?,      // interno  PLE 20
    val isc: Monto?,                          // interno  PLE 21
    val icbper: Monto?,                       // interno  PLE 22
    val otrosTributosCargos: Monto?,          // interno  PLE 23
    val importeTotal: Monto,                  // interno  PLE 24
    val moneda: String?,                      // interno  PLE 25
    val tipoCambio: String?,                  // interno  PLE 26  TODO(spec: REG-145)
    val documentoModificadoFecha: Fecha?,     // interno  PLE 27  TODO(spec: REG-144)
    val documentoModificadoTipo: String?,     // interno  PLE 28
    val documentoModificadoSerie: String?,    // interno  PLE 29
    val codigoDependenciaAduanera: String?,   // interno  PLE 30
    val documentoModificadoNumero: String?,   // interno  PLE 31
    val detraccionFecha: Fecha?,              // interno  PLE 32
    val detraccionNumero: String?,            // interno  PLE 33
    val marcaRetencion: String?,              // interno  PLE 34
    val clasificacionBienesServicios: String?,// interno  PLE 35
    val contratoProyecto: String?,            // interno  PLE 36
    val errorTipo1: String?,                  // interno  PLE 37
    val errorTipo2: String?,                  // interno  PLE 38
    val errorTipo3: String?,                  // interno  PLE 39
    val errorTipo4: String?,                  // interno  PLE 40
    val indicadorMediosPago: String?,         // interno  PLE 41
    val estadoAnotacion: String,              // interno  PLE 42  TODO(spec: REG-146)
)

data class RegistroCompras81Dto(
    val periodo: Periodo,               // interno  PLE 1
    val rucAdquirente: Ruc,             // interno
    val razonSocial: String?,           // interno
    val filas: List<FilaCompras81Dto>,  // interno
)

/** 12.1 según Git/FORMATO_12_1.pdf ("ítem" = x-item-121). Tablas 5, 6 y 12 PENDIENTE. */
data class MovimientoKardex121Dto(
    val fecha: Fecha,             // interno  ítem det-a
    val tipoDocumento: String?,   // interno  ítem det-b (Tabla 10)
    val serie: String?,           // interno  ítem det-c
    val numero: String?,          // interno  ítem det-d
    val tipoOperacion: String,    // interno  ítem det-e (Tabla 12, PENDIENTE)
    val entradas: Cantidad?,      // interno  ítem det-f (incluye saldo inicial)  TODO(spec: REG-148)
    val salidas: Cantidad?,       // interno  ítem det-g
    val saldoFinal: String?,      // interno  ítem det-h
    val origen: Origen?,          // interno
)

data class Totales121Dto(
    val entradas: Cantidad,       // interno  ítem det-i  TODO(spec: REG-148)
    val salidas: Cantidad,        // interno  ítem det-i
    val saldoFinal: String,       // interno  ítem det-i
)

data class Existencia121Dto(
    val codigoExistencia: String,               // MT-070  ítem cab-e (Tabla 5 PENDIENTE)
    val descripcion: String,                    // MT-069  ítem cab-f
    val unidadMedida: String,                   // MT-050  ítem cab-g (Tabla 6 PENDIENTE)
    val movimientos: List<MovimientoKardex121Dto>, // interno
    val totales: Totales121Dto,                 // interno  ítem det-i
)

data class RegistroInventario121Dto(
    val denominacion: String?,                     // interno  ítem cab-a
    val periodo: Periodo,                          // interno  ítem cab-b  TODO(spec: REG-142)
    val ruc: Ruc,                                  // MT-073  ítem cab-c
    val razonSocial: String,                       // MT-075  ítem cab-c
    val establecimientoCodigo: CodigoEstablecimiento, // MT-076  ítem cab-d
    val establecimientoDescripcion: String?,       // interno  ítem cab-d
    val existencias: List<Existencia121Dto>,       // interno
)
