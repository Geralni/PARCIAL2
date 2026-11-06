# ADR-001: Monolito MVC modular

- **Estado:** Aceptado (Fase 1)
- **Contexto:** El caso exige un "monolito MVC limpio, desacoplable hacia Hexagonal/Clean y luego microservicios" (R-03). ABC es una empresa mediana, el equipo es pequeño y hay que operar sin conexión en Android (R-04). Los microservicios desde el día 1 añadirían red, despliegue y consistencia distribuida sin un beneficio inmediato.
- **Decisión:** Un **único desplegable por plataforma**, organizado en **módulos por contexto delimitado** (Emisión, Tributación/Catálogos, Inventario, Registros, Integración SUNAT/OSE, Migración). Dentro de cada módulo se aplica MVC en el borde (View = Compose, Controller = adaptadores de entrada) y un *Model* separado en `application` (casos de uso) y `domain` (Kotlin puro).
- **Reglas para que el monolito sea "limpio":**
  1. El dominio no depende de frameworks (ni Compose, ni Ktor, ni SQL, ni XML).
  2. Un módulo no accede a las tablas de otro: usa su puerto de entrada o un evento.
  3. Un esquema de base de datos por módulo, aunque compartan el mismo archivo SQLite.
  4. Los nombres de los paquetes coinciden con los contextos ([mvc-hexagonal.md §4](../mvc-hexagonal.md)).
- **Consecuencias:**
  - (+) Se despliega con un solo MSI o APK. Las transacciones son locales y simples (el correlativo es atómico, REG-034).
  - (+) La extracción a microservicios es mecánica: cada costura ya existe.
  - (−) Exige disciplina: las reglas 2 y 3 deben verificarse en la Fase 2 con pruebas de arquitectura (por ejemplo, Konsist o ArchUnit).
- **Alternativas descartadas:** microservicios desde el inicio (complejidad operativa sin equipo de plataforma) y un MVC clásico con *Model* = ORM (acopla el dominio a la persistencia y bloquea la ruta hacia hexagonal).
