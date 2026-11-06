# ADR-003: Stack multiplataforma y empaquetado MSI/APK

- **Estado:** Aceptado (Fase 1). Opción elegida por el líder del equipo en el PASO 1.
- **Contexto:** Debe ser nativo en Windows y Android, con distribución MSI (escritorio) y APK (Android) (R-04), un núcleo compartido (dominio y reglas), operación sin conexión (ADR-006) y manejo de XML UBL con firma XMLDSig.

## Opciones comparadas

| Criterio | **A. Kotlin + Compose Multiplatform** | B. .NET MAUI (C#) | C. Flutter (Dart) |
|---|---|---|---|
| Código compartido entre Windows y Android | Dominio, aplicación y UI (Compose) | Dominio, aplicación y UI (XAML) | Dominio, aplicación y UI |
| **MSI** | Sí, nativo: `nativeDistributions { targetFormats(TargetFormat.Msi) }` (con `jpackage` + WiX) | El formato por defecto es MSIX. Para MSI hace falta un proyecto WiX aparte | No es nativo. Requiere WiX o Inno Setup aparte, o el paquete `msix` |
| **APK** | Sí (Android Gradle Plugin) | Sí | Sí |
| XML y XMLDSig | En escritorio, JVM: `javax.xml.crypto` (JSR 105) y librerías maduras. En Android hay que verificar el soporte de `javax.xml.crypto`; se mitiga firmando en el nodo Windows (ADR-006) | `System.Security.Cryptography.Xml` (escritorio). El soporte en Android hay que verificarlo | Ecosistema de firma XML más limitado |
| Servidor HTTP embebido (sincronización) | Ktor | ASP.NET Core (Kestrel) | Paquete `shelf`, menos maduro |
| Manual de Nubefact (referencia) | Trae ejemplo en Java | Trae ejemplos en C# y VB.NET | No trae ejemplo |
| Entorno disponible | Java 25 ya instalado | Requiere instalar el SDK de .NET | Requiere instalar el SDK de Flutter |
| Tamaño del instalador | Mayor (JRE embebido) | Medio | Medio |

## Decisión

**Opción A: Kotlin + Compose Multiplatform.** Es la única que genera **MSI de forma nativa** con su herramienta estándar y APK con la misma base de código. Además, permite poner dominio y aplicación en Kotlin común (`shared/`) y tiene un ecosistema JVM maduro para UBL y XMLDSig en el nodo Windows.

## Especificación del empaquetado (no se construye en la Fase 1)

| Artefacto | Especificación |
|---|---|
| MSI | `packageName = "ABC Facturacion Electronica"`. `packageVersion` sigue SemVer, y MSI exige el formato `MAJOR.MINOR.BUILD`. `upgradeUuid` es fijo. Se instala por usuario o por máquina (a decidir en la Fase 2). Se agregan un acceso directo y una entrada en el menú Inicio. El JRE se recorta con los módulos `java.xml`, `java.xml.crypto`, `java.sql` y `jdk.crypto.ec` (lista **a verificar** en la Fase 2). Firma Authenticode del instalador |
| APK | `applicationId = pe.abc.fe`. `minSdk` y `targetSdk` se definen en la Fase 2. Se firma con el *keystore* de publicación (fuera del repositorio). Se activan R8 y ofuscación |
| CI | Un *pipeline* con dos *jobs*: `packageMsi` (en un agente Windows con WiX) y `assembleRelease` (en un agente con el Android SDK) |

## Consecuencias

- (+) Un solo lenguaje y los DTOs compartidos ([`../../02-dominio-y-contratos/dtos/`](../../02-dominio-y-contratos/dtos/)).
- (−) Se depende de WiX en el agente de construcción y el MSI es más grande por el JRE.
- (−) El soporte de XMLDSig en Android es incierto: por eso **la firma ocurre en el nodo Windows o en el OSE** (ADR-004, ADR-006).
