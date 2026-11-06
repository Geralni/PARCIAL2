# Arquitectura: MVC con visión hexagonal

> **Entregable 2.** Contexto, capas MVC, hexágono, evolución a microservicios y despliegue en Windows (MSI) y Android (APK).
> **Decisiones:** [ADR-001](adr/ADR-001-monolito-mvc-modular.md) (monolito MVC modular), [ADR-002](adr/ADR-002-puertos-y-adaptadores.md) (puertos y adaptadores), [ADR-003](adr/ADR-003-stack-y-empaquetado.md) (Kotlin + Compose Multiplatform, MSI/APK), [ADR-004](adr/ADR-004-ose-vs-sunat-y-firma.md) (OSE y firma), [ADR-005](adr/ADR-005-estrategia-migracion.md) (migración), [ADR-006](adr/ADR-006-operacion-sin-conexion-android.md) (sin conexión en Android), [ADR-007](adr/ADR-007-generacion-ubl-con-clases-del-xsd.md) (UBL con clases del XSD; validar antes de firmar).
> **Idea central:** en una app nativa, **el contrato real es el puerto de entrada** (un caso de uso invocado en el mismo proceso por la UI). HTTP es **solo un adaptador más**: lo usan los dispositivos Android para sincronizar con el nodo Windows y, en el futuro, los microservicios.

## 1. Diagrama de contexto

```mermaid
flowchart LR
  subgraph ABC["ABC Software Corp"]
    U1["Cajero / vendedor<br/>(Android, APK)"]
    U2["Administración y contabilidad<br/>(Windows, MSI)"]
    SIS["Sistema de Facturación Electrónica ABC<br/>(monolito modular Kotlin)"]
    LEG[("Fichas de almacén<br/>legado")]
  end
  OSE["OSE<br/>(Operador de Servicios Electrónicos)"]
  SUNAT["SUNAT<br/>(SEE-Del contribuyente, padrón RUC)"]
  PSE["Proveedor de mercado<br/>p. ej. Nubefact (referencia)"]
  ADQ["Adquirente<br/>(cliente)"]

  U1 -- "emite boletas/facturas<br/>incluso sin conexión" --> SIS
  U2 -- "series, notas, bajas, resúmenes,<br/>registros 14.1/8.1/12.1, migración" --> SIS
  LEG -- "importación única (ADR-005)" --> SIS
  SIS -- "XML UBL firmado / ticket" --> OSE
  OSE -- "CDR" --> SIS
  OSE -- "reenvía" --> SUNAT
  SIS -. "alternativa: SUNAT directo (ADR-004)" .-> SUNAT
  SIS -. "alternativa: JSON vía adaptador de mapeo" .-> PSE
  SIS -- "consulta RUC (ValidadorRucPort)" --> SUNAT
  SIS -- "representación impresa / XML" --> ADQ
```

## 2. Capas MVC (vista del monolito)

El MVC se aplica **en el borde**, y el *Model* se descompone en dominio y aplicación para que no dependa del framework.

```mermaid
flowchart TB
  subgraph V["VIEW (Compose Multiplatform)"]
    V1["Pantallas: Emitir, Comprobantes,<br/>Series, Bajas, Resúmenes, Registros, Migración"]
  end
  subgraph C["CONTROLLER (adaptadores de entrada)"]
    C1["Controladores de UI<br/>(estado de pantalla → comando)"]
    C2["Controladores HTTP Ktor<br/>(openapi.yaml)"]
    C3["Planificador / cola<br/>(reintentos, resúmenes)"]
  end
  subgraph M["MODEL"]
    direction TB
    M1["Aplicación: casos de uso = puertos de entrada<br/>EmitirComprobanteUseCase, ComunicarBajaUseCase, ..."]
    M2["Dominio: agregados, value objects, reglas REG-xxx<br/>(Kotlin puro, sin dependencias)"]
    M1 --> M2
  end
  subgraph I["INFRAESTRUCTURA (adaptadores de salida)"]
    I1["SQLite/SQLDelight<br/>repositorios"]
    I2["Generador UBL (clases xjc) → validador XSD → firmador XMLDSig"]
    I3["Cliente OSE / SUNAT / Nubefact"]
    I4["Importador legado, exportador de registros"]
  end
  V1 --> C1
  C1 --> M1
  C2 --> M1
  C3 --> M1
  M1 -->|"puertos de salida (interfaces)"| I
```

**Regla de dependencias:** `View → Controller → Application → Domain`. La infraestructura implementa interfaces declaradas en *Application*. El dominio no importa nada de Compose, Ktor, SQL ni XML. Esto permite **cambiar MVC por Clean/Hexagonal sin tocar el dominio** (ADR-001).

## 3. Hexágono: puertos y adaptadores

```mermaid
flowchart LR
  subgraph IN["Adaptadores de entrada"]
    UI["UI Compose<br/>(Windows / Android)"]
    HTTP["API HTTP Ktor<br/>(openapi.yaml)"]
    JOB["Planificador / cola offline"]
  end
  subgraph HEX["Núcleo (application + domain)"]
    direction TB
    subgraph PE["Puertos de entrada = casos de uso"]
      P1["EmitirComprobante (CU-01)"]
      P2["ConsultarComprobante (CU-02)"]
      P3["EmitirNota (CU-03/04)"]
      P4["ComunicarBaja (CU-05)"]
      P5["EnviarResumenDiario (CU-06)"]
      P6["GestionarSeries (CU-07)"]
      P7["ConsultarCatalogo (CU-08)"]
      P8["ValidarDocumentoIdentidad (CU-09)"]
      P9["ImportarLegado (CU-10)"]
      P10["GenerarRegistro (CU-11)"]
      P11["ReintentarEnvio / Sincronizar (CU-12)"]
      P12["GestionarProductos (CU-13)"]
    end
    D["Dominio<br/>Comprobante, Nota, Serie, Producto, ..."]
  end
  subgraph OUT["Puertos de salida → adaptadores"]
    R["Repositorios<br/>(Comprobante, Serie, Producto, Movimiento)"]
    UBL["GeneradorUblPort<br/>→ clases xjc del XSD (ADR-007)"]
    XSD["ValidadorXsdPort<br/>XSD ANTES de firmar (REG-094)"]
    FIR["FirmadorXmlPort<br/>→ XMLDSig (almacén seguro SO)"]
    CLI["ClienteSunatOsePort<br/>→ OSE | SUNAT | Nubefact"]
    RUC["ValidadorRucPort<br/>→ padrón SUNAT"]
    IMP["ImportadorLegadoPort<br/>→ CSV/Excel de fichas"]
    REG["GeneradorRegistrosPort<br/>→ 14.1 / 8.1 / 12.1"]
    CAT["CatalogoRepositoryPort + ParametrosTributariosPort"]
    COLA["ColaEnvioPort + IdempotenciaPort"]
  end
  UI --> PE
  HTTP --> PE
  JOB --> PE
  PE --> D
  PE --> R & UBL & XSD & FIR & CLI & RUC & IMP & REG & CAT & COLA
```

El detalle de cada puerto, con sus firmas Kotlin y su operación HTTP, está en [`../04-api/puertos.md`](../04-api/puertos.md).

## 4. Estructura de módulos (costuras ya marcadas)

```
abc-fe/                                   (Gradle multi-módulo, Kotlin)
  shared/
    domain/{emision,tributacion,inventario,registros,migracion,integracion}   ← Kotlin común, sin dependencias
    application/{emision,...}             ← puertos de entrada (casos de uso) y de salida (interfaces)
    adapters-persistence/                 ← SQLDelight (SQLite) — un esquema POR contexto
    adapters-ubl/                         ← GeneradorUbl + Firmador (JVM desktop)
    adapters-sunat/{ose,sunat-directo,nubefact}
  desktopApp/  (Compose Desktop + Ktor server)  → MSI
  androidApp/  (Compose Android)                → APK
```

**Costuras:** (1) un paquete por contexto en `domain` y `application`. (2) Un esquema de base de datos por contexto, sin *joins* entre contextos. (3) Comunicación entre contextos solo por puertos de entrada o eventos (`EventosDominioPort`, [modelo-dominio.md §5](../02-dominio-y-contratos/modelo-dominio.md)). (4) Ningún DTO de un contexto en la firma de otro, salvo los de `comun`.

## 5. Ruta de transición MVC → Hexagonal

El sistema **nace como MVC** (fase 0) y llega a **hexagonal** en pasos pequeños y verificables, sin reescribir el dominio. Cada paso tiene un criterio de salida comprobable, y el siguiente no empieza hasta cumplirlo.

```mermaid
flowchart LR
  P0["Fase 0: MVC clásico<br/>View → Controller → Model<br/>(Model = dominio + aplicación + acceso a datos)"]
  P1["Paso 1: separar el Model<br/>domain (Kotlin puro) / application / infraestructura"]
  P2["Paso 2: casos de uso = puertos de entrada<br/>los Controllers solo llaman a *UseCase"]
  P3["Paso 3: puertos de salida<br/>interfaces en application; JDBC, UBL, firma y OSE pasan a adaptadores"]
  P4["Paso 4: inversión de dependencias<br/>composition root; el dominio no importa infraestructura"]
  P5["Paso 5: Ktor = otro adaptador de entrada<br/>la UI y HTTP comparten los mismos puertos"]
  P6["Hexagonal estricto<br/>pruebas de arquitectura en CI"]
  P0 --> P1 --> P2 --> P3 --> P4 --> P5 --> P6
```

| Paso | Qué cambia | Qué NO cambia | Criterio de salida (verificable) |
|---|---|---|---|
| **0. MVC** (punto de partida) | Pantallas Compose (View), controladores de pantalla (Controller) y *Model* con entidades, reglas y repositorios juntos. Es lo que se entrega primero, porque es simple para el equipo | — | La emisión de una factura funciona de punta a punta |
| **1. Separar el Model** | El *Model* se divide en `domain` (agregados, value objects, reglas REG-xxx), `application` (orquestación) e `infra` (SQL, XML) | Pantallas y controladores | `domain` compila sin dependencias de Compose, Ktor, SQL ni JAXB |
| **2. Puertos de entrada** | Cada acción de un controlador pasa a ser un `*UseCase` (tabla de [puertos.md §1](../04-api/puertos.md)). El controlador solo traduce pantalla ↔ comando | Las reglas del dominio | Ningún controlador accede a un repositorio directamente |
| **3. Puertos de salida** | Se declaran interfaces (`SerieRepositoryPort`, `GeneradorUblPort`, `ValidadorXsdPort`, `FirmadorXmlPort`, `ClienteSunatOsePort`, …) en `application`. Las implementaciones pasan a `adapters-*` | Los casos de uso, que solo dependen de interfaces | Los casos de uso se prueban con adaptadores falsos, sin base de datos ni red |
| **4. Inversión de dependencias** | Un *composition root* por plataforma (desktopApp y androidApp) conecta cada puerto con su adaptador. En Android, `ClienteSunatOsePort` va hacia el nodo Windows (ADR-006) | Dominio y casos de uso | Cambiar el adaptador OSE por el de SUNAT directo es un cambio de configuración (ADR-004) |
| **5. HTTP como adaptador** | Se agrega Ktor ([openapi.yaml](../04-api/openapi.yaml)) **sobre los mismos puertos** que usa la UI | Los puertos | Cada `operationId` declara su `x-puerto-entrada` (lo verifica `validar_contratos.py`, V3) |
| **6. Hexagonal estricto** | Las reglas de dependencia se vuelven pruebas automáticas (Konsist o ArchUnit) en CI, junto con el *outbox* de eventos | — | Construir el proyecto falla si `domain` importa infraestructura o si un módulo lee las tablas de otro (ADR-001) |

**Equivalencia MVC ↔ Hexagonal:** View + Controller = adaptadores de entrada. *Model* = `application` (puertos de entrada) + `domain`. El acceso a datos, UBL, la firma y el OSE, que en MVC vivían "dentro del Model", quedan como **adaptadores de salida** detrás de puertos.

## 6. Ruta de evolución hacia microservicios (después del hexagonal)

```mermaid
flowchart LR
  subgraph F1["Fase actual: monolito modular"]
    MONO["Monolito Kotlin<br/>módulos: Emisión | Tributación | Inventario |<br/>Registros | Integración | Migración<br/>(eventos en proceso)"]
  end
  subgraph F2["Fase 2: hexagonal estricto"]
    MONO2["Mismo despliegue<br/>+ outbox de eventos<br/>+ esquemas BD separados"]
  end
  subgraph F3["Fase 3: microservicios candidatos"]
    S1["Emisión"]
    S2["Tributación / Catálogos"]
    S3["Inventario"]
    S4["Registros (lectura)"]
    S5["Integración SUNAT/OSE"]
    S6["Migración (temporal)"]
    BUS(["Bus de eventos"])
  end
  MONO --> MONO2 --> F3
  S1 -- ComprobanteEmitido --> BUS
  BUS --> S5
  S5 -- ComprobanteAceptado --> BUS
  BUS --> S3 & S4
  S1 -- "consulta tasas" --> S2
  S6 -- LoteLegadoImportado --> BUS
```

| Microservicio candidato | Se extrae primero porque… | Puerto que se convierte en API remota |
|---|---|---|
| **Integración SUNAT/OSE** | Es el más volátil (proveedor, latencia, reintentos) y escala distinto. | `ClienteSunatOsePort` → servicio de envíos |
| **Tributación/Catálogos** | Es de solo lectura, cambia por norma y lo comparte todo el sistema. | `CatalogoRepositoryPort`, `ParametrosTributariosPort` |
| **Registros** | Es CQRS puro (proyecciones por período). | `GenerarRegistroUseCase` |
| **Migración** | Es temporal y se puede apagar al terminar. | `ImportarLegadoUseCase` |
| **Inventario** | Se acopla a Emisión solo por eventos. | `MovimientoRepositoryPort` |
| **Emisión** | Es el núcleo: se extrae al final. | `EmitirComprobanteUseCase` |

## 7. Despliegue: Windows (MSI) y Android (APK)

```mermaid
flowchart TB
  subgraph WIN["PC Windows (local principal) — instalador MSI"]
    WUI["desktopApp (Compose Desktop)<br/>JRE embebido (jpackage)"]
    WCORE["shared: domain + application"]
    WAPI["Ktor HTTP (adaptador)<br/>solo red local / VPN"]
    WDB[("SQLite<br/>carpeta de datos del usuario")]
    WCERT["Certificado digital<br/>almacén de Windows (CNG/DPAPI)"]
    WUI --> WCORE
    WAPI --> WCORE
    WCORE --> WDB
    WCORE --> WCERT
  end
  subgraph AND["Dispositivo Android — APK"]
    AUI["androidApp (Compose)"]
    ACORE["shared: domain + application"]
    ADB[("SQLite cifrada<br/>+ cola de envío")]
    AKS["Android Keystore<br/>(claves de cifrado local)"]
    AUI --> ACORE --> ADB
    ACORE --> AKS
  end
  OSE["OSE / SUNAT"]
  ACORE -- "HTTPS: sincronizar lote<br/>(POST /sincronizacion/lotes)" --> WAPI
  WCORE -- "XML firmado" --> OSE
```

**Especificación de empaquetado** (no se construyen instaladores en la Fase 1):

| Plataforma | Artefacto | Herramienta | Contenido | Requisitos del entorno de construcción |
|---|---|---|---|---|
| Windows 10/11 x64 | `.msi` | Plugin Compose Multiplatform `nativeDistributions` (`TargetFormat.Msi`), que usa `jpackage` | App + JRE recortado + SQLite. `upgradeUuid` fijo para que las actualizaciones reemplacen la versión anterior. Firma de código Authenticode (certificado de código, **distinto** del certificado de facturación) | JDK 17 o superior y **WiX Toolset** (lo exige `jpackage` para generar MSI) |
| Android 8.0 o superior (minSdk a definir) | `.apk` (y `.aab` para tienda) | Android Gradle Plugin | App + SQLite cifrada | Android SDK. El APK se firma con el *keystore* de publicación |

Los **requisitos no funcionales** de despliegue están en [00-analisis-del-caso.md](../00-analisis-del-caso.md) (RNF-02 y RNF-03).
