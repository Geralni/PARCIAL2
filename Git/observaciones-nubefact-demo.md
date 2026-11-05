# Nubefact DEMO — observaciones de la interfaz (capturas del 27/10/2026)

**Uso:** insumo para `01-casos-de-uso.md`, `06-migracion/mapeo-legado.md` y la matriz de trazabilidad.
**Alcance de este archivo:** solo lo que se vio en pantalla. No incluye datos personales, direcciones ni credenciales. La pantalla de API (con ruta y token) se excluyó a propósito.
**Cuenta:** modo de prueba. Un banner permanente ofrece «Activar con la SUNAT (Modo Producción)», es decir, la cuenta tiene un modo de prueba y un modo de producción.

## 1. Navegación y módulos

Mosaico del escritorio: Punto de Venta, Comprobantes, Catálogo, Entidades, Guías de Remisión, Compras, Retenciones, Percepciones, Resúmenes de Boletas, Configuración Principal, Usuarios, Locales y Series, Cuentas Bancarias, API (Integración) y Mi Cuenta.
El menú superior añade Anulaciones, Reportes, Monitoreo, Tickets y un selector de local.
**Dentro del alcance de la Fase 1:** emisión, catálogo, entidades, series, anulaciones, resúmenes y reportes. **Fuera:** guías, retenciones y percepciones (basta con anotar que existen).

## 2. Emitir comprobante electrónico

Pantalla única para factura, boleta y notas. Campos de cabecera:

| Campo en pantalla | Observación |
|---|---|
| Cliente | Buscador con botón «+ Nuevo cliente». Existe un cliente genérico «VARIOS» (documento «-») |
| Tipo de documento | Factura electrónica por defecto; el selector permite cambiar a nota de crédito (visto) |
| Serie | Desplegable (ej. la de prueba) |
| Número (Referencial) | Solo lectura: lo asigna el sistema al emitir |
| Fecha de emisión | Tres selectores (día, mes, año). Por defecto, hoy |
| IGV % | Lista con 18 % por defecto y un enlace «Más info» |
| Tipo de operación | Lista con códigos de dos dígitos, ej. «VENTA INTERNA [01]» |
| Moneda y Tipo de cambio | Soles por defecto. Tipo de cambio editable |
| Fecha de vencimiento | Tres selectores |
| ¿Pagado? | Interruptor Sí/No |
| Agregar línea o ítem | Abre un formulario de línea (**no se capturó**) |
| Enlaces | Guía de remisión, Orden de compra/servicio, Placa de vehículo, Medios de Pago, Formato de PDF |
| Observaciones | Texto libre |
| Interruptores especiales | ¿Detracción?, ¿Bienes Región Selva?, ¿Servicios Región Selva? |

**Panel de totales (calculado, solo lectura):** % descuento global, descuento global, descuento por ítem, descuento total, anticipo, exonerada, inafecta, gravada, IGV, gratuita, otros cargos (el único editable), **ICBPER** y total. **No hay una fila de ISC** en este panel, aunque el manual de la API sí maneja `total_isc` y `tipo_de_isc` por ítem.
**Botones:** «Guardar como borrador» y «Generar comprobante». Existe, por tanto, el estado **borrador** además del emitido.

**Al elegir «Nota de crédito»** cambia el formulario:
- Aparecen «Documento a modificar», «Serie» y «Número del documento a modificar».
- Aparece «Tipo Nota de Crédito» (desplegable).
- Desaparece el interruptor de detracción y quedan los dos de región selva.
- El botón pasa a «Crear Documento».

## 3. Medios de pago (ventana emergente)

Campos: Tipo (ej. «POR PAGAR [CRÉDITO]»), Importe y Fecha de cuota, con botón para eliminar y «Agregar medio de pago». Implica **forma de pago (contado o crédito) con varias cuotas**, cada una con importe y fecha.

## 4. Catálogo de productos y servicios

Campos: Categoría, **Tipo** (producto o servicio), **Código interno**, **Nombre** (estos tres obligatorios), **Código de Producto SUNAT** (campo nuevo con buscador), Moneda (referencial), Tipo de afectación (opcional), valores de **venta** (sin IGV y con IGV) y de **compra** (sin IGV y con IGV), y un interruptor «Destacado para Punto de Venta».
Observación: los precios son opcionales en el catálogo, y la afectación del IGV también.

## 5. Entidades (clientes y proveedores)

Campos: Número (RUC, DNI, etc.) obligatorio, con botón **EXTRAER** que parece autocompletar los datos; Tipo (obligatorio); Razón social o nombre completo (obligatorio); Razón comercial; Dirección fiscal; email principal y dos emails opcionales; móvil; fijo; N.º de cuenta de detracción del cliente; detalle adicional; licencia de conducir; placa del vehículo; MTC.
Observación: el módulo se llama «Entidades» y no «Clientes», lo que sugiere que sirve también para proveedores (por confirmar). Incluye datos de transporte (licencia, placa, MTC) que no hacen falta en el alcance.

## 6. Locales y series

Una tabla por **local** (código interno, descripción, **código SUNAT del establecimiento**, UBIGEO INEI, departamento, provincia, distrito, dirección y columna «Offline»). Dentro de cada local hay **series por tipo de comprobante**:

- Factura, nota de crédito y nota de débito: misma serie (prefijo `F`).
- Boleta, nota de crédito y nota de débito: misma serie (prefijo `B`).
- Retención (`R`), percepción (`P`), guía remitente (`T`) y guía transportista (`V`).
- **Series de contingencia** numéricas (`0001`) para factura, boleta y sus notas.

Observaciones: las series cuelgan del **local**; las notas reutilizan la serie del documento que modifican; la pantalla muestra «Locales disponibles: 4» y ofrece «Ver todas las series de este local».

## 7. Consolidado de facturas, boletas y notas

Aviso: muestra los comprobantes de **todos los locales o puntos de emisión** de la empresa. Filtros: rango de fechas, tipo y entidad; botones «Filtrar», **«Descarga Excel»** y «Buscar Documento». La lista estaba vacía («No existen registros»), por lo que no se vieron los estados ni las opciones de descarga.

## 8. Comunicaciones de baja

Aviso en pantalla: la baja consta de **2 pasos**: (1) agregar o elegir un documento y (2) consultar el estado de la anulación a la SUNAT. Botón «Agregar documento para ANULAR o COMUNICAR DE BAJA». Filtros por fechas y por estado: **Aceptadas, Pendientes y Rechazadas**.

## 9. API (Integración): solo estructura

Se necesitan tres cosas: una RUTA, un TOKEN y un archivo plano (JSON o TXT). Hay manuales para facturas, boletas y notas (JSON y TXT), guías, retenciones y percepciones, además de ejemplos de código. Se pueden crear varios tokens por local, con descripción. **Los valores no se registran.**

## 10. Qué le falta al software legado de ABC (frente a lo observado)

1. Series y correlativos por local y tipo de documento.
2. Validación y consulta de RUC o DNI.
3. Cálculo de IGV, ISC e ICBPER, y panel de totales por tipo de afectación.
4. Estados del comprobante (borrador, emitido, aceptado, rechazado, anulado) y comunicación de baja asíncrona.
5. Forma de pago con cuotas.
6. Código de producto SUNAT y unidad de medida estandarizada.
7. Operación en contingencia (series propias) y modo sin conexión.
8. Exportación a Excel y base para los registros de ventas (14.1).

## 11. Pendiente de capturar

Ventana «Agregar línea o ítem» (unidad, afectación IGV, ISC), un comprobante emitido (estado y descargas PDF, XML y CDR), Resúmenes de Boletas, y la nota de débito.
