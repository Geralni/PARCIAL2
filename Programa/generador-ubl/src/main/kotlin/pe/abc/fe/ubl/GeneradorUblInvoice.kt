package pe.abc.fe.ubl

import jakarta.xml.bind.JAXBContext
import jakarta.xml.bind.Marshaller
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.AddressType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.AttachmentType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.CommodityClassificationType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.CustomerPartyType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.ExternalReferenceType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.InvoiceLineType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.ItemIdentificationType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.ItemType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.MonetaryTotalType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PartyIdentificationType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PartyLegalEntityType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PartyNameType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PartyType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PaymentTermsType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PriceType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.PricingReferenceType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.SignatureType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.SupplierPartyType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.TaxCategoryType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.TaxSchemeType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.TaxSubtotalType
import oasis.names.specification.ubl.schema.xsd.commonaggregatecomponents_2.TaxTotalType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.AddressTypeCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.BaseUnitMeasureType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.CustomizationIDType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.DescriptionType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.DocumentCurrencyCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.DueDateType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.IDType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.InvoiceTypeCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.InvoicedQuantityType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.IssueDateType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.IssueTimeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.ItemClassificationCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.LineCountNumericType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.LineExtensionAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.NameType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.NoteType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PayableAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PaymentDueDateType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PaymentMeansIDType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PerUnitAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PercentType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PriceAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.PriceTypeCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.RegistrationNameType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TaxAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TaxExemptionReasonCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TaxInclusiveAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TaxTypeCodeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TaxableAmountType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.TierRangeType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.UBLVersionIDType
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.URIType
import oasis.names.specification.ubl.schema.xsd.invoice_2.InvoiceType
import oasis.names.specification.ubl.schema.xsd.invoice_2.ObjectFactory
import pe.abc.fe.aplicacion.GeneradorUblPort
import pe.abc.fe.dominio.AfectacionIgv
import pe.abc.fe.dominio.ComprobanteCalculado
import pe.abc.fe.dominio.FormaPago
import pe.abc.fe.dominio.LineaCalculada
import pe.abc.fe.dominio.SistemaIsc
import pe.abc.fe.dominio.SubtotalTributo
import pe.abc.fe.dominio.TipoPrecio
import pe.abc.fe.dominio.Tributo
import java.io.StringWriter
import java.math.BigDecimal
import java.time.format.DateTimeFormatter
import javax.xml.datatype.DatatypeFactory
import oasis.names.specification.ubl.schema.xsd.commonbasiccomponents_2.AmountType as CbcAmountType
import un.unece.uncefact.data.specification.corecomponenttypeschemamodule._2.AmountType as CctAmountType

/** Asigna valor y moneda (@currencyID) a cualquier monto UBL (REG-069: una sola moneda por documento). */
private fun <T : CctAmountType> T.importe(valor: BigDecimal, moneda: String): T = also { it.value = valor; it.currencyID = moneda }

/**
 * Adaptador GeneradorUblPort (ADR-007): ComprobanteCalculado -> clases JAXB generadas desde
 * UBL-Invoice-2.1.xsd -> XML. Nunca arma el XML a mano (sin DOM ni plantillas).
 *
 * Estructura según la validación SUNAT vigente (Git/XSL Actualizado al 06092022, DISC-25):
 * emisor y adquirente en PartyIdentification/PartyLegalEntity, tipo de operación en
 * InvoiceTypeCode/@listID (MT-087). Los valores de atributos (listName, schemeURI…) son los que
 * exigen las expresiones regulares de ValidaExprRegFactura-2.0.1.xsl.
 *
 * Fuera de alcance de este parcial: ext:UBLExtensions/ds:Signature (la firma la agrega FirmadorXmlPort, REG-090).
 */
class GeneradorUblInvoice : GeneradorUblPort {

    private val contexto: JAXBContext = JAXBContext.newInstance(ObjectFactory::class.java)
    private val fechas = DatatypeFactory.newInstance()

    override fun generar(comprobante: ComprobanteCalculado): String {
        val invoice = construirInvoice(comprobante)
        val marshaller = contexto.createMarshaller().apply {
            setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true)
            setProperty(Marshaller.JAXB_ENCODING, "UTF-8")
            setProperty(PrefijosUbl.PROPIEDAD, PrefijosUbl())
        }
        return StringWriter().also { marshaller.marshal(ObjectFactory().createInvoice(invoice), it) }.toString()
    }

    internal fun construirInvoice(cc: ComprobanteCalculado): InvoiceType {
        val c = cc.comprobante
        val moneda = c.moneda
        return InvoiceType().apply {
            setUBLVersionID(UBLVersionIDType().apply { value = "2.1" })                  // MT-002, REG-001
            setCustomizationID(CustomizationIDType().apply { value = "2.0"; schemeAgencyName = SUNAT }) // MT-003, REG-002
            setID(IDType().apply { value = c.numero })                                   // MT-006
            setIssueDate(IssueDateType().apply { value = fechas.newXMLGregorianCalendar(c.fechaEmision.toString()) }) // MT-007
            c.horaEmision?.let { h -> setIssueTime(IssueTimeType().apply { value = fechas.newXMLGregorianCalendar(h.format(HORA)) }) } // MT-008, REG-082
            c.fechaVencimiento?.let { f -> setDueDate(DueDateType().apply { value = fechas.newXMLGregorianCalendar(f.toString()) }) }
            setInvoiceTypeCode(InvoiceTypeCodeType().apply {                             // MT-010 + MT-087
                value = c.tipo.codigo
                listID = c.tipoOperacion
                listAgencyName = SUNAT
                listName = "Tipo de Documento"
                listURI = CATALOGO + "01"
                name = "Tipo de Operacion"
                listSchemeURI = CATALOGO + "51"
            })
            c.leyendas.forEach { l -> note.add(NoteType().apply { value = l.texto; languageLocaleID = l.codigo }) } // MT-011/012
            setDocumentCurrencyCode(DocumentCurrencyCodeType().apply {                   // MT-013
                value = moneda
                listID = "ISO 4217 Alpha"
                listName = "Currency"
                listAgencyName = UNECE
            })
            setLineCountNumeric(LineCountNumericType().apply { value = BigDecimal(cc.lineas.size) }) // MT-014
            signature.add(firma(c.emisor.ruc, c.emisor.razonSocial))                      // MT-020
            setAccountingSupplierParty(SupplierPartyType().apply { party = parteEmisor(cc) })
            setAccountingCustomerParty(CustomerPartyType().apply { party = parteAdquirente(cc) })
            paymentTerms.addAll(formaPago(cc))
            taxTotal.add(TaxTotalType().apply {                                           // MT-034..040
                taxAmount = TaxAmountType().importe(cc.totales.totalTributos, moneda)
                cc.subtotales.forEach { s -> taxSubtotal.add(subtotalCabecera(s, moneda)) }
            })
            setLegalMonetaryTotal(MonetaryTotalType().apply {                             // MT-041..046
                lineExtensionAmount = LineExtensionAmountType().importe(cc.totales.valorVenta, moneda)
                taxInclusiveAmount = TaxInclusiveAmountType().importe(cc.totales.precioVenta, moneda)
                payableAmount = PayableAmountType().importe(cc.totales.importeTotal, moneda)
            })
            cc.lineas.forEach { l -> invoiceLine.add(linea(l, moneda)) }
        }
    }

    // ---------------- Partes ----------------

    private fun firma(ruc: String, razonSocial: String) = SignatureType().apply {
        val id = "SIGN-$ruc"
        setID(IDType().apply { value = id })
        signatoryParty = PartyType().apply {
            partyIdentification.add(PartyIdentificationType().apply { setID(IDType().apply { value = ruc }) })
            partyName.add(PartyNameType().apply { name = NameType().apply { value = razonSocial } })
        }
        digitalSignatureAttachment = AttachmentType().apply {
            externalReference = ExternalReferenceType().apply { uri = URIType().apply { value = "#$id" } }
        }
    }

    private fun parteEmisor(cc: ComprobanteCalculado) = PartyType().apply {
        val e = cc.comprobante.emisor
        partyIdentification.add(identificacion(e.ruc, "6"))                               // MT-073, MT-074
        e.nombreComercial?.let { nc -> partyName.add(PartyNameType().apply { name = NameType().apply { value = nc } }) } // MT-021
        partyLegalEntity.add(PartyLegalEntityType().apply {
            registrationName = RegistrationNameType().apply { value = e.razonSocial }   // MT-075
            registrationAddress = AddressType().apply {
                e.ubigeo?.let { u -> setID(IDType().apply { value = u; schemeName = "Ubigeos"; schemeAgencyName = "PE:INEI" }) } // MT-077
                addressTypeCode = AddressTypeCodeType().apply {                          // MT-076
                    value = e.codigoEstablecimiento
                    listAgencyName = SUNAT
                    listName = "Establecimientos anexos"
                }
            }
        })
    }

    private fun parteAdquirente(cc: ComprobanteCalculado) = PartyType().apply {
        val a = cc.comprobante.adquirente
        partyIdentification.add(identificacion(a.numeroDocumento, a.tipoDocumento))      // MT-078, MT-079
        partyLegalEntity.add(PartyLegalEntityType().apply {
            registrationName = RegistrationNameType().apply { value = a.razonSocial }    // MT-088
        })
    }

    private fun identificacion(numero: String, tipoDocumento: String) = PartyIdentificationType().apply {
        setID(IDType().apply {
            value = numero
            schemeID = tipoDocumento
            schemeName = "Documento de Identidad"
            schemeAgencyName = SUNAT
            schemeURI = CATALOGO + "06"
        })
    }

    // ---------------- Forma de pago (MT-193..MT-196) ----------------

    private fun formaPago(cc: ComprobanteCalculado): List<PaymentTermsType> {
        val moneda = cc.comprobante.moneda
        fun termino(medio: String) = PaymentTermsType().apply {
            setID(IDType().apply { value = "FormaPago" })
            paymentMeansID.add(PaymentMeansIDType().apply { value = medio })
        }
        return when (val fp = cc.comprobante.formaPago) {
            FormaPago.Contado -> listOf(termino("Contado"))
            is FormaPago.Credito -> listOf(termino("Credito").apply { amount = CbcAmountType().importe(cc.totales.importeTotal, moneda) }) +
                fp.cuotas.mapIndexed { i, q ->
                    termino("Cuota" + (i + 1).toString().padStart(3, '0')).apply {
                        amount = CbcAmountType().importe(q.monto, moneda)
                        paymentDueDate = PaymentDueDateType().apply { value = fechas.newXMLGregorianCalendar(q.fechaVencimiento.toString()) }
                    }
                }
        }
    }

    // ---------------- Tributos ----------------

    private fun esquema(t: Tributo) = TaxSchemeType().apply {
        setID(IDType().apply {
            value = t.codigo
            schemeName = "Codigo de tributos"
            schemeAgencyName = SUNAT
            schemeURI = CATALOGO + "05"
        })
        name = NameType().apply { value = t.nombre }
        taxTypeCode = TaxTypeCodeType().apply { value = t.codigoInternacional }
    }

    private fun subtotalCabecera(s: SubtotalTributo, moneda: String) = TaxSubtotalType().apply {
        if (s.tributo != Tributo.ICBPER) taxableAmount = TaxableAmountType().importe(s.base, moneda)
        taxAmount = TaxAmountType().importe(s.monto, moneda)
        taxCategory = TaxCategoryType().apply { taxScheme = esquema(s.tributo) }
    }

    private fun linea(l: LineaCalculada, moneda: String) = InvoiceLineType().apply {
        val d = l.linea
        setID(IDType().apply { value = l.numeroOrden.toString() })                        // MT-048
        invoicedQuantity = InvoicedQuantityType().apply {                                // MT-049, MT-050
            value = d.cantidad
            unitCode = d.unidadMedida
            unitCodeListID = "UN/ECE rec 20"
            unitCodeListAgencyName = UNECE
        }
        lineExtensionAmount = LineExtensionAmountType().importe(l.valorVenta, moneda) // MT-051
        pricingReference = PricingReferenceType().apply {                                 // MT-052, MT-053
            alternativeConditionPrice.add(PriceType().apply {
                priceAmount = PriceAmountType().importe(l.precioUnitario, moneda)
                priceTypeCode = PriceTypeCodeType().apply {
                    value = TipoPrecio.PRECIO_UNITARIO_CON_IGV.codigo
                    listName = "Tipo de Precio"
                    listAgencyName = SUNAT
                    listURI = CATALOGO + "16"
                }
            })
        }
        taxTotal.add(TaxTotalType().apply {                                               // MT-059..068
            taxAmount = TaxAmountType().importe(l.totalTributos, moneda)
            if (l.isc.signum() > 0) taxSubtotal.add(subtotalIsc(l, moneda))
            taxSubtotal.add(subtotalAfectacion(l, moneda))
            if (l.icbper.signum() > 0) taxSubtotal.add(subtotalIcbper(l, moneda))
        })
        item = ItemType().apply {
            description.add(DescriptionType().apply { value = d.descripcion })           // MT-069
            d.codigoProducto?.let { cod ->                                                // MT-070
                sellersItemIdentification = ItemIdentificationType().apply { setID(IDType().apply { value = cod }) }
            }
            d.codigoProductoSunat?.let { cod ->                                           // MT-071
                commodityClassification.add(CommodityClassificationType().apply {
                    itemClassificationCode = ItemClassificationCodeType().apply {
                        value = cod
                        listID = "UNSPSC"
                        listAgencyName = "GS1 US"
                        listName = "Item Classification"
                    }
                })
            }
        }
        price = PriceType().apply { priceAmount = PriceAmountType().importe(d.valorUnitario, moneda) } // MT-072
    }

    /** IGV, exonerado, inafecto o exportación según el catálogo 07 (MT-064, REG-016, REG-022). */
    private fun subtotalAfectacion(l: LineaCalculada, moneda: String) = TaxSubtotalType().apply {
        val gravada = l.linea.afectacionIgv == AfectacionIgv.GRAVADO_ONEROSA
        taxableAmount = TaxableAmountType().importe(if (gravada) l.baseIgv else l.valorVenta, moneda)
        taxAmount = TaxAmountType().importe(l.igv, moneda)
        taxCategory = TaxCategoryType().apply {
            percent = PercentType().apply { value = l.tasaIgv }                          // MT-063
            taxExemptionReasonCode = TaxExemptionReasonCodeType().apply {
                value = l.linea.afectacionIgv.codigo
                listAgencyName = SUNAT
                listName = "Afectacion del IGV"
                listURI = CATALOGO + "07"
            }
            taxScheme = esquema(l.linea.afectacionIgv.tributo)
        }
    }

    /** ISC con su sistema de cálculo del catálogo 08 en cbc:TierRange (MT-065, punto clave del caso). */
    private fun subtotalIsc(l: LineaCalculada, moneda: String) = TaxSubtotalType().apply {
        val isc = l.linea.isc!!
        taxableAmount = TaxableAmountType().importe(l.valorVenta, moneda)
        taxAmount = TaxAmountType().importe(l.isc, moneda)
        taxCategory = TaxCategoryType().apply {
            if (isc.sistema != SistemaIsc.MONTO_FIJO) percent = PercentType().apply { value = isc.tasaOMonto }
            tierRange = TierRangeType().apply { value = isc.sistema.codigo }
            taxScheme = esquema(Tributo.ISC)
        }
    }

    /** ICBPER: cantidad de bolsas (NIU) y monto unitario en TaxCategory/PerUnitAmount (MT-190..MT-192). */
    private fun subtotalIcbper(l: LineaCalculada, moneda: String) = TaxSubtotalType().apply {
        taxAmount = TaxAmountType().importe(l.icbper, moneda)
        baseUnitMeasure = BaseUnitMeasureType().apply { value = BigDecimal(l.linea.bolsasPlastico); unitCode = "NIU" }
        taxCategory = TaxCategoryType().apply {
            perUnitAmount = PerUnitAmountType().importe(l.montoUnitarioIcbper, moneda)
            taxScheme = esquema(Tributo.ICBPER)
        }
    }

    private companion object {
        const val SUNAT = "PE:SUNAT"
        const val UNECE = "United Nations Economic Commission for Europe"
        const val CATALOGO = "urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo"
        val HORA: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss")
    }
}
