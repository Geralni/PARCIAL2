package pe.abc.fe.dominio

/**
 * Códigos SUNAT usados por el dominio (Anexo 8; ver specs/02-dominio-y-contratos/catalogs/INDEX.md).
 * Los catálogos chicos y estables se modelan como enum; los grandes se cargan de resources/catalogos/catNN.json.
 */

/** Catálogo 01 (solo los tipos del alcance de la raíz Invoice). */
enum class TipoComprobante(val codigo: String, val letraSerie: Char) {
    FACTURA("01", 'F'),
    BOLETA("03", 'B'),
}

/** Catálogo 05: tributos. [codigo] -> TaxScheme/cbc:ID, [nombre] -> cbc:Name, [codigoInternacional] -> cbc:TaxTypeCode. */
enum class Tributo(val codigo: String, val nombre: String, val codigoInternacional: String) {
    IGV("1000", "IGV", "VAT"),
    ISC("2000", "ISC", "EXC"),
    ICBPER("7152", "ICBPER", "OTH"),
    EXPORTACION("9995", "EXP", "FRE"),
    EXONERADO("9997", "EXO", "VAT"),
    INAFECTO("9998", "INA", "FRE"),
}

/**
 * Catálogo 07: afectación del IGV (operaciones onerosas del alcance de la Fase 2).
 * [tributo] es la relación afectación -> tributo del catálogo 07 (REG-022).
 * Las afectaciones gratuitas (11-16, 21, 31-37) quedan fuera: requieren valor referencial (REG-055).
 */
enum class AfectacionIgv(val codigo: String, val tributo: Tributo) {
    GRAVADO_ONEROSA("10", Tributo.IGV),
    EXONERADO_ONEROSA("20", Tributo.EXONERADO),
    INAFECTO_ONEROSA("30", Tributo.INAFECTO),
    EXPORTACION("40", Tributo.EXPORTACION),
}

/** Catálogo 08: sistema de cálculo del ISC -> cbc:TierRange (MT-065, REG-017, REG-052). */
enum class SistemaIsc(val codigo: String) {
    AL_VALOR("01"),
    MONTO_FIJO("02"),
    PRECIO_VENTA_PUBLICO("03"),
}

/** Catálogo 16: tipo de precio -> cbc:PriceTypeCode (MT-053). */
enum class TipoPrecio(val codigo: String) {
    PRECIO_UNITARIO_CON_IGV("01"),
}

/** Catálogos grandes leídos de resources/catalogos/catNN.json (copias de specs/.../catalogs). */
object CatalogosSunat {
    private val regexCodigo = Regex("\"codigo\"\\s*:\\s*\"([^\"]+)\"")

    private fun codigos(numero: String): Set<String> {
        val recurso = "/catalogos/cat$numero.json"
        val texto = CatalogosSunat::class.java.getResourceAsStream(recurso)
            ?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
            ?: error("No se encontró el catálogo $recurso")
        // Solo los códigos de 'items' (después de la clave "items").
        val items = texto.substringAfter("\"items\"")
        return regexCodigo.findAll(items).map { it.groupValues[1] }.toSet()
    }

    val monedas: Set<String> by lazy { codigos("02") }
    val unidadesMedida: Set<String> by lazy { codigos("03") }
    val documentosIdentidad: Set<String> by lazy { codigos("06") }
    val tiposOperacion: Set<String> by lazy { codigos("51") }
    val leyendas: Set<String> by lazy { codigos("52") }
}
