package pe.abc.fe.dominio

import java.math.BigDecimal

/**
 * Reglas de negocio que el XSD NO valida (mapa-xsd.md §3), aplicadas ANTES de generar el XML.
 * Cada violación cita su regla de reglas-de-validacion.md.
 */
object ValidadorComprobante {
    private val ruc = Regex("^\\d{11}$")
    private val dni = Regex("^\\d{8}$")
    private val serieContingencia = Regex("^\\d{4}$")
    private val establecimiento = Regex("^\\d{4}$")
    private val ubigeo = Regex("^\\d{6}$")
    private val codigoProductoSunat = Regex("^\\d{8}$")

    fun violaciones(c: Comprobante): List<Violacion> = buildList {
        // Series y correlativo
        val serieElectronica = Regex("^${c.tipo.letraSerie}[A-Z0-9]{3}$")
        if (!serieElectronica.matches(c.serie) && !serieContingencia.matches(c.serie)) {
            val regla = if (c.tipo == TipoComprobante.FACTURA) "REG-030" else "REG-031"
            add(Violacion(regla, "serie", "La serie '${c.serie}' no corresponde a ${c.tipo}: debe ser ${c.tipo.letraSerie}### o NNNN (contingencia)"))
        }
        if (c.correlativo !in 1..99_999_999) add(Violacion("REG-035", "correlativo", "Debe estar entre 1 y 99999999"))

        // Emisor
        if (!ruc.matches(c.emisor.ruc)) add(Violacion("REG-040", "emisor.ruc", "El RUC debe tener 11 dígitos"))
        if (c.emisor.razonSocial.isBlank() || c.emisor.razonSocial.length > 100) add(Violacion("REG-100", "emisor.razonSocial", "Obligatorio, hasta 100 caracteres"))
        if (!establecimiento.matches(c.emisor.codigoEstablecimiento)) add(Violacion("REG-036", "emisor.codigoEstablecimiento", "Debe tener 4 dígitos"))
        c.emisor.ubigeo?.let { if (!ubigeo.matches(it)) add(Violacion("REG-038", "emisor.ubigeo", "El ubigeo debe tener 6 dígitos")) }

        // Adquirente
        val a = c.adquirente
        if (a.tipoDocumento !in CatalogosSunat.documentosIdentidad) add(Violacion("REG-015", "adquirente.tipoDocumento", "'${a.tipoDocumento}' no pertenece al catálogo 06"))
        if (a.tipoDocumento == "6" && !ruc.matches(a.numeroDocumento)) add(Violacion("REG-042", "adquirente.numeroDocumento", "Con tipo 6 (RUC) el número debe tener 11 dígitos"))
        if (a.tipoDocumento == "1" && !dni.matches(a.numeroDocumento)) add(Violacion("REG-043", "adquirente.numeroDocumento", "Con tipo 1 (DNI) el número debe tener 8 dígitos"))
        val esExportacion = c.tipoOperacion.startsWith("02") || c.tipoOperacion.startsWith("04")
        if (c.tipo == TipoComprobante.FACTURA && a.tipoDocumento != "6" && !esExportacion) {
            add(Violacion("REG-044", "adquirente.tipoDocumento", "La factura exige un adquirente con RUC (tipo 6), salvo exportación o no domiciliados"))
        }
        if (a.razonSocial.isBlank() || a.razonSocial.length > 100) add(Violacion("REG-100", "adquirente.razonSocial", "Obligatorio, hasta 100 caracteres"))

        // Cabecera
        if (c.moneda !in CatalogosSunat.monedas) add(Violacion("REG-011", "moneda", "'${c.moneda}' no pertenece al catálogo 02"))
        if (c.tipoOperacion !in CatalogosSunat.tiposOperacion) add(Violacion("REG-021", "tipoOperacion", "'${c.tipoOperacion}' no pertenece al catálogo 51"))
        c.fechaVencimiento?.let { if (it.isBefore(c.fechaEmision)) add(Violacion("REG-081", "fechaVencimiento", "No puede ser anterior a la fecha de emisión")) }
        c.leyendas.forEachIndexed { i, l ->
            if (l.codigo !in CatalogosSunat.leyendas) add(Violacion("REG-025", "leyendas[$i].codigo", "'${l.codigo}' no pertenece al catálogo 52"))
            if (l.texto.isBlank() || l.texto.length > 100) add(Violacion("REG-008", "leyendas[$i].texto", "Obligatorio, hasta 100 caracteres"))
        }

        // Líneas
        if (c.lineas.isEmpty() || c.lineas.size > 999) add(Violacion("REG-006", "lineas", "Debe haber entre 1 y 999 líneas"))
        c.lineas.forEachIndexed { i, l ->
            val campo = "lineas[$i]"
            if (l.cantidad.signum() <= 0) add(Violacion("REG-067", "$campo.cantidad", "Debe ser mayor que 0"))
            if (l.valorUnitario.signum() < 0) add(Violacion("REG-067", "$campo.valorUnitario", "No puede ser negativo"))
            if (l.unidadMedida !in CatalogosSunat.unidadesMedida) add(Violacion("REG-012", "$campo.unidadMedida", "'${l.unidadMedida}' no pertenece al catálogo 03"))
            if (l.descripcion.isBlank() || l.descripcion.length > 250) add(Violacion("REG-100", "$campo.descripcion", "Obligatoria, hasta 250 caracteres"))
            l.codigoProductoSunat?.let { if (!codigoProductoSunat.matches(it)) add(Violacion("REG-027", "$campo.codigoProductoSunat", "Debe tener 8 dígitos (UNSPSC)")) }
            l.isc?.let { isc ->
                if (l.afectacionIgv != AfectacionIgv.GRAVADO_ONEROSA) add(Violacion("REG-017", "$campo.isc", "El ISC solo se modela en líneas gravadas"))
                if (isc.tasaOMonto.signum() <= 0) add(Violacion("REG-052", "$campo.isc.tasaOMonto", "Debe ser mayor que 0"))
                if (isc.sistema == SistemaIsc.PRECIO_VENTA_PUBLICO && (isc.precioVentaPublico == null || isc.precioVentaPublico.signum() <= 0)) {
                    add(Violacion("REG-052", "$campo.isc.precioVentaPublico", "El sistema 03 exige el precio de venta al público"))
                }
            }
            if (l.bolsasPlastico < 0) add(Violacion("REG-054", "$campo.bolsasPlastico", "No puede ser negativo"))
        }

        // Forma de pago
        val fp = c.formaPago
        if (fp is FormaPago.Credito) {
            if (fp.cuotas.isEmpty()) add(Violacion("REG-028", "formaPago.cuotas", "El crédito exige al menos una cuota"))
            fp.cuotas.forEachIndexed { i, q ->
                if (q.monto.signum() <= 0) add(Violacion("REG-029", "formaPago.cuotas[$i].monto", "Debe ser mayor que 0"))
                if (!q.fechaVencimiento.isAfter(c.fechaEmision)) add(Violacion("REG-029", "formaPago.cuotas[$i].fechaVencimiento", "Debe ser posterior a la fecha de emisión"))
            }
        }
    }

    /** La suma de cuotas debe igualar el monto neto pendiente (REG-029); se valida tras calcular el total. */
    fun violacionesDeCuotas(c: Comprobante, importeTotal: BigDecimal): List<Violacion> {
        val fp = c.formaPago as? FormaPago.Credito ?: return emptyList()
        val suma = fp.cuotas.fold(BigDecimal.ZERO) { acc, q -> acc + q.monto }
        return if (suma.compareTo(importeTotal) != 0) {
            listOf(Violacion("REG-029", "formaPago.cuotas", "La suma de cuotas ($suma) debe ser igual al monto neto pendiente ($importeTotal)"))
        } else emptyList()
    }
}
