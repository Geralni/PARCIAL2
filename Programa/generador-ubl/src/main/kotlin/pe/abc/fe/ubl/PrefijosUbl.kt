package pe.abc.fe.ubl

import org.glassfish.jaxb.runtime.marshaller.NamespacePrefixMapper

/** Prefijos habituales de UBL/SUNAT (cac, cbc, ext, ds, sac) en lugar de ns1, ns2… */
class PrefijosUbl : NamespacePrefixMapper() {
    override fun getPreferredPrefix(namespaceUri: String, suggestion: String?, requirePrefix: Boolean): String? =
        PREFIJOS[namespaceUri] ?: suggestion

    override fun getPreDeclaredNamespaceUris(): Array<String> = PREFIJOS.keys.filter { it.isNotEmpty() }.toTypedArray()

    companion object {
        const val PROPIEDAD = "org.glassfish.jaxb.namespacePrefixMapper"
        private val PREFIJOS = mapOf(
            "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" to "",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" to "cac",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" to "cbc",
            "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" to "ext",
            "http://www.w3.org/2000/09/xmldsig#" to "ds",
        )
    }
}
