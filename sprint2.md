# Sprint 2 – Porvoz: Llamadas Automáticas de Voz

---

# 1. Caso de Negocio

## 1.1 Descripción del Negocio

Porvoz es una plataforma que llama por teléfono a pacientes para recordarles sus medicamentos. La idea nace de un problema concreto: muchos adultos mayores olvidan sus tomas porque manejan varios horarios al día, no recuerdan cuál fue la última o no son cercanos a la tecnología. Eso lleva a tratamientos a medias, recaídas y hospitalizaciones que se pudieron evitar.

El cuidador (familiar, hijo o personal de salud) tampoco puede estar pendiente de cada toma. La llamada de Porvoz cubre ese hueco: se programa una vez con el medicamento, dosis y horario, y a partir de ahí el sistema llama solo. Si el paciente no contesta o dice que no tomó, el sistema reprograma y le avisa al cuidador.

Para el paciente todo pasa por voz, no necesita abrir una app ni revisar el celular. El cuidador entra a la web cuando quiere y ve el historial completo: qué llamadas se hicieron, qué respondió cada vez y qué alertas se generaron.

### Misión

Que los pacientes no olviden sus medicamentos y los cuidadores puedan saber, sin tener que estar presentes, si la toma se cumplió.

### Visión

Ser la herramienta que cuidadores y centros de salud usan primero cuando necesitan asegurar la adherencia a un tratamiento.

---

## 1.2 Análisis del Mercado

Según la **OMS (2003)**, cerca del **50% de los pacientes con enfermedades crónicas** no toma su tratamiento como debería. Estudios del NIH ubican esa cifra entre 30% y 50%, y la relacionan con complicaciones médicas y hospitalizaciones que en muchos casos se podían evitar.

En Colombia, según el **DANE (2023)**, hay más de **5.7 millones de personas de 65 años o más**, y es el grupo donde más se concentran los tratamientos con varios medicamentos al día. Buena parte vive sola o con cuidadores que trabajan, así que no hay quien acompañe cada toma.

Las apps con notificaciones móviles ayudan, pero hay que tener el celular a la mano, ver la pantalla y reaccionar. Es fácil ignorarlas y para una persona mayor con poca experiencia digital es aún más complicado. La llamada en cambio entra sola y se atiende por voz, sin abrir nada.

**Segmentos objetivo:** adultos mayores con tratamientos diarios, pacientes con enfermedades crónicas, familiares y cuidadores que no pueden estar presentes en cada toma, y centros geriátricos o clínicas ambulatorias.

---

## 1.3 Producto o Servicio

El cuidador entra a la web, registra al paciente, agrega los medicamentos con su dosis, horario e instrucciones, y a partir de ahí Porvoz se encarga de llamar. Si el paciente confirma, se guarda. Si no contesta o dice que no tomó, el sistema reintenta y le avisa al cuidador. Todo el historial queda en su cuenta para revisar después.

Hay tres planes: **Básico** gratuito (1 paciente), **Familiar** (hasta 3) y **Profesional** 

**Propuesta de valor:** la llamada llega sola, sin que el paciente tenga que abrir la app o ver una notificación. El cuidador no necesita estar pendiente de cada toma: el sistema le avisa solo cuando algo sale mal.

---

## 1.4 Finanzas

### 1.4.1 Presupuesto Pre-Operación

| Rubro | Unidad | Costo unitario (COP) | Cantidad | Subtotal (COP) |
|-------|--------|----------------------|----------|----------------|
| **PERSONAL** | | | | |
| Desarrollador backend | mes | 1.462.000 | 1 | 1.462.000 |
| Desarrollador fullstack | mes | 1.462.000 | 1 | 1.462.000 |
| QA / Tester | mes | 1.462.000 | 1 | 1.462.000 |
| Product Manager | mes | 1.462.000 | 1 | 1.462.000 |
| **Subtotal Personal** | | | | **5.848.000** |
| **EQUIPOS** | | | | |
| Portátiles (cada miembro usa el propio) | — | 0 | — | 0 |
| **Subtotal Equipos** | | | | **0** |
| **LICENCIAS Y ACTIVOS DIGITALES** | | | | |
| Twilio — crédito inicial para pruebas (~$20 USD) | unidad | 84.000 | 1 | 84.000 |
| Google Gemini API — crédito inicial (~$10 USD) | unidad | 42.000 | 1 | 42.000 |
| GitHub Team (4 usuarios, 1 mes) | mes | 67.000 | 1 | 67.000 |
| **Subtotal Licencias** | | | | **193.000** |
| **REGISTRO DE PROPIEDAD INTELECTUAL** | | | | |
| Registro de dominio .com (1 año) | unidad | 50.000 | 1 | 50.000 |
| **Subtotal Registro PI** | | | | **50.000** |
| **PUBLICIDAD** | | | | |
| Material digital básico (presentaciones, diseño) | unidad | 100.000 | 1 | 100.000 |
| **Subtotal Publicidad** | | | | **100.000** |
| | | | | |
| **TOTAL PRE-OPERACIÓN** | | | | **6.191.000** |

---

### 1.4.2 Presupuesto de Operación

Una vez el producto está listo para salir al mercado, se necesita sostener su funcionamiento mes a mes. Los costos se dividen en fijos (se mantienen) y variables (dependen del plan y uso). Todos los valores están en COP.

#### Costos Fijos Mensuales

| Rubro | Valor mensual (COP) |
|-------|---------------------|
| Servidor en la nube | 63.000 |
| Base de datos en la nube | 63.000 |
| Almacenamiento de audios y registros | 8.400 |
| Dominio .com (prorrateado mensual) | 4.200 |
| Número de teléfono en Twilio (número EE.UU.) | 5.000 |
| Gemini API | 10.000 |
| GitHub Team | 84.000 |
| Correos transaccionales | 42.000 |
| **TOTAL COSTOS FIJOS** | **279.600** |

> Nota: se usa un número de EE.UU. en Twilio ($1.15/mes) en lugar de uno colombiano ($14/mes). Los pacientes lo pueden guardar en contactos; las llamadas salen igualmente desde "Porvoz". Gemini API es gratuito hasta mas o menos 7.500 clasificaciones/mes, que cubre todos los planes actuales; se reservan 10.000 COP como colchón para crecimiento.+

#### Costos Variables por Plan (uso mensual)

El costo por llamada se calcula con la tarifa real de Twilio para móviles colombianos ($0.0377 USD/min ≈ 158 COP/min a la tasa de cambio de 4.200 COP/USD), una duración promedio de **20 segundos** por llamada y un colchón del 35% para llamadas fallidas y reintentos.

- Costo base por minuto: **158 COP**
- Costo base por llamada (20 s): **53 COP**
- Costo operativo estimado por llamada (con 35% de colchón): **75 COP**

Los límites de llamadas se diseñaron para cubrir el caso real del producto: un paciente con entre 4 y 6 medicamentos al día genera entre 5 y 7 llamadas diarias contando reintentos, lo que equivale a ~150–210 llamadas al mes. Para pacientes con regímenes más complejos (8–15 medicamentos) el plan Profesional ofrece más capacidad por paciente.

| Plan | Límite de llamadas/mes | Costo variable estimado (COP) |
|------|------------------------|-------------------------------|
| **Básico** | 150 | 11.250 |
| **Familiar** | 500 | 37.500 |
| **Profesional** | 3.000 | 225.000 |

#### Planes y Proyección de Ingresos

| Plan | Descripción | Precio/mes (COP) | Costo variable (COP) | Margen por cliente |
|------|-------------|------------------|----------------------|--------------------|
| **Básico** | 1 paciente, hasta 150 llamadas/mes | 0 | 11.250 | -11.250 |
| **Familiar** | Hasta 3 pacientes, 500 llamadas/mes | 59.900 | 37.500 | 22.400 |
| **Profesional** | Hasta 20 pacientes, 3.000 llamadas/mes | 299.900 | 225.000 | 74.900 |

**Punto de equilibrio (mensual):** con costos fijos de 279.600 COP.

- Solo Familiar: 279.600 / 22.400 = **13 clientes** (aprox.).
- Solo Profesional: 279.600 / 74.900 = **4 clientes** (aprox.).

**Escenario rentable de referencia:** 8 clientes Familiar + 2 clientes Profesional.

- Margen Familiar: 8 × 22.400 = 179.200
- Margen Profesional: 2 × 74.900 = 149.800
- Margen total: **329.000 COP/mes**

Resultado: **329.000 - 279.600 = 49.400 COP/mes** (operación en positivo).

---

## 1.5 Riesgos

### 1.5.1 Inventario de Riesgos

| Código | Riesgo | Descripción | Probabilidad | Impacto |
|--------|--------|-------------|--------------|---------|
| R1 | Falla del servicio de llamadas | El proveedor de llamadas cae por más de 4 horas | Poco Probable | Crítico |
| R2 | Cambio de normativa | Una nueva ley exige permisos adicionales para llamadas automáticas | Posible | Crítico |
| R3 | Pocos clientes al inicio | Menos de 5 clientes en los primeros 2 meses | Muy Probable | Moderado |
| R4 | Competencia con más recursos | Un competidor lanza algo similar con más inversión | Posible | Moderado |
| R5 | Mala calidad de audio en redes lentas | La llamada no se entiende bien en zonas con señal débil | Poco Probable | Moderado |
| R6 | Aumento de costos del proveedor | El precio por llamada sube más del 30% | Posible | Marginal |
| R7 | Datos de pacientes expuestos | Un error de configuración expone información de salud | Raro | Catastrófico |
| R8 | Salida de un desarrollador clave | El desarrollador que conoce el módulo de llamadas se va | Posible | Moderado |
| R9 | Problemas legales con datos de salud | El sistema almacena datos sin los permisos correctos | Raro | Crítico |
| R10 | El sistema no aguanta muchos usuarios | Con más de 500 clientes el sistema se cae | Poco Probable | Crítico |

---

### 1.5.2 Matriz de Probabilidad e Impacto

| | Despreciable | Marginal | Moderado | Crítico | Catastrófico |
|---|---|---|---|---|---|
| **Seguro** | Mínimo | Moderado | Alto | Extremo | Extremo |
| **Muy Probable** | Mínimo | Bajo | **R3** Moderado | Moderado | Extremo |
| **Posible** | Mínimo | **R6** Bajo | **R4, R8** Moderado | **R2** Alto | Extremo |
| **Poco Probable** | Mínimo | Bajo | **R5** Bajo | **R1, R10** Moderado | Alto |
| **Raro** | Mínimo | Mínimo | Bajo | **R9** Moderado | **R7** Alto |

---

### 1.5.3 Matriz RACI

| Actividad | Product Owner | Scrum Master | Tech Lead | Stakeholder |
|-----------|:-------------:|:------------:|:---------:|:-----------:|
| Identificar riesgos | A | R | C | I |
| Evaluar probabilidad e impacto | I | A | R | C |
| Definir estrategias de mitigación | C | A | R | I |
| Asignar responsable por riesgo | A | R | C | I |
| Hacer seguimiento de riesgos activos | I | R | A | I |
| Comunicar cuando ocurre un riesgo | I | R | A | C |
| Revisar y actualizar el inventario | C | A | R | I |

---

### 1.5.4 Estrategias de Mitigación

| Código | Riesgo | Estrategia | Responsable |
|--------|--------|------------|-------------|
| R1 | Falla del servicio de llamadas | Tener configurado un proveedor alternativo; alertas automáticas si no hay respuesta en 5 minutos | Tech Lead |
| R2 | Cambio de normativa | Revisar periódicamente las regulaciones de telecomunicaciones en Colombia; consultar con un abogado antes del lanzamiento | Product Owner |
| R3 | Pocos clientes al inicio | Hacer prueba piloto con al menos dos centros geriátricos antes del mes 3 | Product Owner |
| R4 | Competencia con más recursos | Mantener diferenciación en la facilidad de uso y en el manejo de respuestas con IA | Product Owner |
| R5 | Mala calidad de audio | Hacer pruebas en redes móviles deficientes antes de cada entrega | Tech Lead |
| R6 | Aumento de costos del proveedor | Buscar contratos con descuento por volumen cuando haya más de 50 clientes | Product Owner |
| R7 | Datos expuestos | Revisar la configuración de permisos en cada sprint; cifrar la información de salud en base de datos | Tech Lead |
| R8 | Salida de un desarrollador clave | Documentar el módulo de llamadas detalladamente; hacer revisiones de código en equipo | Scrum Master |
| R9 | Problemas legales con datos de salud | Revisar con un abogado qué permisos necesita el sistema antes del lanzamiento | Product Owner |
| R10 | Sistema no aguanta muchos usuarios | Hacer pruebas de carga antes de lanzar; preparar la configuración para escalar cuando sea necesario | Tech Lead |

---

# 2. Ejecución de Pruebas Automáticas de Software

Las pruebas automáticas cubren la lógica del sistema y se ejecutan cada vez que se cambia código. Las manuales (sección 3) cubren la parte humana: si el cuidador entiende, si encuentra lo que busca, si los textos confunden. Cada historia de usuario tiene al menos un test del caso esperado y otro del caso alternativo, alineados con los criterios de aceptación del backlog.

## 2.1 Estrategia de Pruebas

| Funcionalidad | Tipo de Prueba | Justificación |
|---------------|---------------|---------------|
| **HU-04 – Llamadas automáticas con IA** | | |
| Paciente dice que no → se programa reintento | Unitaria | La lógica de reintento vive en `LlamadaService` sin depender de red; se verifica el conteo y la fecha de la nueva llamada |
| Se superó el máximo de reintentos → no se programa otro | Unitaria | Es la regla central de `max_reintentos`; confirma que el sistema no llama indefinidamente |
| Paciente no contesta → también genera reintento | Unitaria | Verifica la rama `RESPUESTA_NO_ATENDIDA`, que debe disparar el mismo flujo que la negativa |
| El saludo incluye nombre, medicamento e instrucciones | Integración | Verifica que el endpoint de voz arme el TwiML con los datos reales del paciente y el medicamento desde la base de datos |
| **HU-05 – Registrar confirmación de toma** | | |
| Paciente dice "sí" → se registra como confirmada | Unitaria | El clasificador es determinístico; no necesita llamadas reales para verificarse |
| Paciente dice variación coloquial ("ya lo tomé") → se clasifica igual | Unitaria | Cubre variaciones sin tilde y frases informales que un adulto mayor podría decir |
| **HU-09 – Detectar respuestas negativas** | | |
| Paciente dice "no" simple → clasificado como negativa | Unitaria | Verifica que el texto más corto posible de negación se detecte correctamente |
| Paciente dice "después" → clasificado como aplazado | Unitaria | Verifica variaciones coloquiales ("en un rato", "más tarde") que indican aplazamiento |
| **HU-30 – Sistema de Notificaciones de Emergencia** | | |
| Paciente reporta síntomas → se crea notificación crítica | Integración | Requiere modelos reales; verifica que la prioridad sea CRÍTICA y el título incluya "EMERGENCIA" |
| Respuesta de emergencia en webhook → alerta crítica creada | Integración | Prueba el flujo completo desde `registrar_respuesta` hasta la notificación en base de datos |
| **HU-31 – Sistema de Acciones Post-Llamada** | | |
| Confirmación → no se crea reintento ni alerta innecesaria | Unitaria | Verifica que el flujo positivo no genera ruido al cuidador |
| Negativa → reintento + alerta al cuidador | Unitaria | Verifica que las dos acciones post-llamada ocurren juntas cuando el paciente dice que no |
| **HU-29 – Historial de llamadas** | | |
| Llamada completada queda almacenada y es consultable | Integración | Verifica que los registros persisten en base de datos y se pueden filtrar por usuario y estado |
| Llamadas con distintos resultados son distinguibles | Integración | Confirma que confirmadas y negativas se pueden separar en consultas, base del historial con filtros |
| **HU-32 – Integración de notificaciones con correo** | | |
| Preferencia activa → `_debe_enviar_email` retorna True | Unitaria | La lógica de preferencias es pura y determinística; se prueba sola sin necesitar SMTP real |
| Preferencia desactivada → `_debe_enviar_email` retorna False | Unitaria | Confirma que el cuidador puede silenciar notificaciones y el sistema lo respeta |
| **HU-11 – Dashboard básico de seguimiento** | | |
| `obtener_datos_completos` retorna estructura con todos los bloques | Integración | Verifica que el servicio del dashboard agrega pacientes, medicamentos, estadísticas y actividad en un solo objeto |
| Estadísticas de llamadas de la semana son correctas | Integración | Confirma los conteos de confirmadas, negativas y no atendidas con datos reales en base de datos |
| **HU-07 – Validación y manejo básico de errores** | | |
| Registro con email duplicado lanza error | Unitaria | La validación de unicidad está en el servicio de registro; se prueba sola para confirmar que bloquea correctamente |
| Fecha de nacimiento inválida retorna mensaje de error | Unitaria | El validador de edad es una función pura; se verifica que formatos incorrectos no pasen |
| **HU-27 – Recuperar contraseña** | | |
| Solicitud de reset con email registrado devuelve respuesta válida | Integración | Verifica que el formulario de recuperación responde 200 o 302 sin errores de servidor |
| Solicitud con email inexistente no expone si el usuario existe | Integración | Prueba de seguridad: la respuesta debe ser igual independientemente de si el email está registrado |
| **Flujo completo entre componentes** | | |
| Paciente dice no → se reprograma la llamada → se crea alerta | Integración | Valida que los tres pasos de la cadena sucedan en orden con datos reales |

Cada historia de usuario tiene al menos una prueba del **caso esperado (happy path)** y una del **caso alternativo o de error**, según los criterios de aceptación definidos en el backlog. HU-34 (responsive) se valida manualmente en las pruebas de usabilidad de la sección 3.

---

## 2.2 Tests Implementados

Los tests están distribuidos en los módulos del proyecto. La suite completa tiene **102 tests** que pasan y se ejecutan automáticamente en cada PR vía GitHub Actions (ver sección 2.3).

| Historia | Tests | Archivos |
|----------|-------|---------|
| HU-04 Llamadas automáticas | 6 | `apps/llamadas/tests/test_services.py` |
| HU-05 Registrar confirmación | 3 | `apps/llamadas/tests/test_webhook_logic.py` |
| HU-07 Validación de errores | 3 | `apps/autenticacion/tests.py`, `apps/core/tests/` |
| HU-09 Respuestas negativas | 2 | `apps/llamadas/tests/test_webhook_logic.py` |
| HU-11 Dashboard | 3 | `apps/dashboard/tests.py` |
| HU-27 Recuperar contraseña | 2 | `apps/autenticacion/tests.py` |
| HU-29 Historial de llamadas | 2 | `apps/llamadas/tests/test_services.py` |
| HU-30 Emergencias | 2 | `apps/llamadas/tests/test_services.py` |
| HU-31 Acciones post-llamada | 2 | `apps/llamadas/tests/test_services.py` |
| HU-32 Notificaciones correo | 2 | `apps/notificaciones/tests/` |
| HU-34 Responsive | — | Se valida manualmente (usabilidad) |

---

### 2.2.1 Ejemplos de Tests Clave

Los siguientes tests están en `apps/llamadas/tests/test_services.py` y son representativos de la estrategia: uno verifica el caso esperado y otro verifica que el sistema se comporte bien cuando algo sale diferente.

**Happy path – el paciente dice que no y el sistema programa un reintento:**

```python
def test_negativa_programa_reintento(self):
    """'No lo tomé' → crea una nueva llamada programada con intentos=1."""
    self.assertEqual(self._llamadas_programadas().count(), 0)
    LlamadaService.registrar_respuesta(
        call_sid="CA_TEST_NEG",
        transcripcion="Usuario: no lo tomé",
        como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
        resultado=RespuestaLlamada.RESULTADO_NEGATIVA,
    )
    nuevas = self._llamadas_programadas()
    self.assertEqual(nuevas.count(), 1)
    self.assertEqual(nuevas.first().intentos, 1)
    delta = nuevas.first().fecha_programada - timezone.now()
    self.assertGreater(delta.total_seconds(), 60 * 5)
    self.assertLess(delta.total_seconds(), 60 * 15)
```

**Flujo alternativo – ya se agotaron los reintentos, no se programa otro:**

```python
def test_reintentos_no_exceden_max(self):
    """Cuando intentos > max_reintentos no se programa otro."""
    self.llamada.intentos = 3  # ya superó max_reintentos=2
    self.llamada.save(update_fields=["intentos"])
    LlamadaService.registrar_respuesta(
        call_sid="CA_TEST_NEG",
        transcripcion="Usuario: no",
        como_respondio=RespuestaLlamada.RESPUESTA_ATENDIDA,
        resultado=RespuestaLlamada.RESULTADO_NEGATIVA,
    )
    self.assertEqual(self._llamadas_programadas().count(), 0)
```

---

### 2.2.2 Evidencia de Ejecución

Los tests se corren desde la carpeta `porvoz/` (la que contiene `manage.py`), con el entorno virtual activado:

```bash
# Desde la raíz del repositorio
cd porvoz
.venv\Scripts\activate          # Windows (PowerShell o CMD)
# source .venv/bin/activate     # macOS / Linux

python manage.py test --verbosity 2
```

Para correr solo los tests del servicio de llamadas:

```bash
python manage.py test apps.llamadas.tests.test_services --verbosity 2
```

[Insertar captura de pantalla de la ejecución en terminal o del resultado verde en GitHub Actions]

---

## 2.3 CI con GitHub Actions

El archivo `.github/workflows/tests.yml` corre automáticamente en cada push y en cada pull request a `main` o `development`. Si algún test falla o la cobertura baja del 80%, el merge queda bloqueado.

Lo que hace el workflow en orden:

1. **Lint con ruff** — verifica estilo antes de correr nada.
2. **Tests con coverage** — `coverage run manage.py test` sobre la suite completa (94 tests).
3. **Reporte de cobertura** — `coverage report --fail-under=80` hace fallar el job si baja del umbral.

```yaml
# .github/workflows/tests.yml (resumen)
on:
  push:
    branches: [main, development]
  pull_request:
    branches: [main, development]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r porvoz/requirements.txt coverage ruff
      - run: ruff check porvoz/apps porvoz/config
      - working-directory: porvoz
        run: |
          coverage run manage.py test --verbosity 2
          coverage report --fail-under=80
```

---

## 2.4 Casos de Prueba (Sprint 2)

Casos de prueba manuales diseñados a partir de los criterios de aceptación. Se ejecutaron junto con los tests automáticos durante el sprint.

| ID | Historia | Pasos | Resultado esperado | Estado |
|----|----------|-------|--------------------|--------|
| CP-01 | HU-04 | Programar un medicamento → esperar a la hora → contestar la llamada y decir "sí" | La llamada queda como `CONFIRMADA` y no se programan reintentos | Pasa |
| CP-02 | HU-04 | Programar un medicamento con `max_reintentos=2` → contestar "no" tres veces seguidas | Después del segundo "no" no se crea otra llamada y se genera una alerta para el cuidador | Pasa |
| CP-03 | HU-05 | En la llamada decir "ya lo tomé" (sin tilde, variación coloquial) | El sistema lo clasifica como confirmación | Pasa |
| CP-04 | HU-09 | En la llamada decir "más tarde" | El sistema lo clasifica como aplazado y reprograma a 10 minutos | Pasa |
| CP-05 | HU-30 | En la llamada decir "me siento mal" | Se genera una alerta de emergencia y se envía correo al cuidador aun si tiene desactivadas notificaciones por email | Pasa |

---

# 3. Protocolo de Pruebas de Usabilidad

Las pruebas están **planeadas en Sprint 2** y se ejecutarán en Sprint 3. El objetivo es probar con cuidadores reales usando el sistema.

## 3.1 Participantes

- **Cantidad:** 8 personas
- **Perfil:** cuidadores reales (familiares o personal de salud), 25 a 65 años, nivel digital básico o medio
- **Exclusión:** personas con experiencia en desarrollo de software o UX

## 3.2 Tareas

Cada tarea representa una acción cotidiana que podría realizar un cuidador dentro de la plataforma. A los participantes se les leerá cada tarea en voz alta, sin explicarles los pasos que deben seguir, con el fin de observar cómo interactúan naturalmente con la interfaz y detectar posibles dificultades de uso.

### **T1 — Registrar un paciente nuevo**
*"Acabas de empezar a usar Porvoz. Tu mamá toma Losartán a las 8 a.m. y a las 8 p.m. Agrégala al sistema con ese medicamento."*

En esta tarea, el participante debe crear el perfil de un paciente nuevo, ingresar el número de teléfono y registrar el medicamento con su nombre, dosis y horarios correspondientes.

Esta es una de las tareas más importantes porque representa el primer flujo completo que un cuidador realiza al entrar a la plataforma por primera vez. Además, permite evaluar si el proceso inicial de registro resulta claro y fácil de seguir.

---

### **T2 — Consultar una llamada que no fue contestada**
*"El sistema intentó llamar anoche y no hubo respuesta. Busca esa llamada y fíjate a qué hora fue y qué dice el resultado."*

Aquí se espera que el participante ingrese al historial de llamadas del paciente, identifique la llamada no contestada del día anterior y revise la información registrada.

El propósito es analizar si el acceso al historial resulta intuitivo o si el usuario presenta dificultades para llegar hasta esa sección.

---

### **T3 — Entender una alerta activa**
*"Tienes una alerta nueva. Ábrela y cuéntame qué medicamento la generó y por qué."*

En esta actividad, el participante debe ubicar la sección de alertas, abrir la notificación pendiente y explicar qué ocurrió: qué paciente está involucrado, qué medicamento generó la alerta y cuál fue la causa.

Esta tarea permite evaluar si la información mostrada en las alertas es suficientemente clara y comprensible sin necesidad de apoyo externo.

---

### **T4 — Cambiar el horario de un medicamento**
*"Tu papá ahora toma el Metformín a las 7 a.m. en vez de las 8. Actualiza ese horario."*

El participante debe localizar al paciente, ingresar a la información del medicamento y modificar el horario de toma previamente registrado.

Con esta tarea se busca evaluar si la opción de edición es visible y si el proceso para actualizar la información resulta sencillo.

---

### **T5 — Agregar un segundo medicamento al mismo paciente**
*"Además del Losartán, tu mamá ahora también toma Atorvastatina todas las noches a las 9 p.m. Agrégalo."*

En este caso, el participante debe volver al perfil del paciente creado anteriormente y añadir un nuevo medicamento con su horario correspondiente.

La tarea sirve para validar si el sistema facilita la gestión de varios medicamentos para un mismo paciente sin generar confusión.

---

### **T6 — Ver el historial de la semana**
*"Quieres saber cuántas llamadas contestó tu paciente esta semana. Encuéntralo."*

El participante debe revisar el historial de llamadas, identificar las correspondientes a los últimos siete días y determinar cuántas fueron contestadas.

Esta tarea ayuda a medir qué tan comprensibles son los filtros y la visualización de registros dentro de la plataforma.

---

### **T7 — Actualizar el teléfono del paciente**
*"Tu mamá cambió de número. El nuevo es 300 111 2233. Actualízalo para que las llamadas lleguen ahí."*

En esta tarea, el participante debe ingresar a la ficha del paciente y modificar el número telefónico registrado.

Aunque parece una acción sencilla, permite identificar si las opciones de edición del perfil están ubicadas de manera clara dentro de la interfaz.

---

### **T8 — Cerrar sesión y volver a entrar**
*"Sal de la aplicación y vuelve a entrar. Confirma que el paciente y el medicamento que registraste antes siguen ahí."*

Aquí el participante debe cerrar sesión, iniciar nuevamente con sus credenciales y verificar que la información registrada anteriormente se haya conservado.

El objetivo es observar si el flujo de autenticación es entendible y si el usuario comprende que los datos permanecen guardados entre sesiones.

---

**Criterio de éxito por tarea:**  
Se considera exitosa cuando el participante logra completarla sin intervención de nosotros.

---

## 3.3 Hipótesis


- **H1:** El flujo de registro inicial, dividido entre la creación del paciente y el registro del medicamento, podría generar dificultades. 

- **H2:** La consulta del historial de llamadas será uno de los puntos más faciles ya que incluso aparece en el sidebar

- **H3:** Las opciones para editar información, como horarios o números telefónicos, pueden pasar desapercibidas, ya que están dentro de la ficha del paciente y no cuentan con accesos visibles desde la lista principal.

---

## 3.4 Preguntas de investigación


1. ¿Qué porcentaje de participantes logra completar cada tarea sin ayuda?
2. ¿En qué parte del registro inicial se presentan más demoras o errores?
3. ¿Cuántos intentos necesita el usuario para llegar al historial de llamadas desde la pantalla principal?
4. ¿Qué botones, textos o secciones generan más dudas durante la sesión?
5. Si el participante pudiera cambiar una sola cosa del sistema, ¿cuál sería?

---

## 3.5 Criterios de evaluación


| Métrica | Cómo se mide | Meta |
|---------|--------------|------|
| Tasa de éxito por tarea | Porcentaje de participantes que completan la tarea sin ayuda | ≥ 75% |
| Tiempo por tarea | Tiempo desde que se lee la tarea hasta que el participante termina | T1 ≤ 4 min / T2–T8 ≤ 3 min |
| Errores de navegación | Número de veces que el usuario entra a una sección equivocada | ≤ 2 |
| Satisfacción general | Encuesta de 1 a 5 al finalizar | ≥ 3.5 |
| Tasa de abandono | Participantes que se rinden o piden ayuda antes de terminar | ≤ 25% |

---

## 3.6 Materiales necesarios para hacer las pruebas
- Plantilla de observación para registrar tiempos, errores y comentarios.
- Encuesta de satisfacción
- Computador

---

## 3.7 Desarrollo de la sesión

Cada sesión tendrá una duración aproximada de **10 a 15 minutos** y se dividirá en los siguientes bloques:

| Bloque | Tiempo | Actividad |
|--------|--------|----------|
| Introducción | 2 min | Explicación del proceso  |
| Exploración libre | 3 min | Navegación inicial sin tareas |
| Tareas T1–T8 | 8 min | Ejecución de tareas mientras se registran tiempos y errores |
| Encuesta | 2 min | Encuesta individual de satisfacción |

### **Responsibilidades de cada integrante que hace la sesion**

- **Facilitador:** leer las tareas y controlar el tiempo sin intervenir.
- **Observador:** registrar errores, tiempos y comentarios relevantes.
- **Analista:** revisar y consolidar la información de la sesion.


Una vez finalizadas las 8 sesiones, se elaborará un reporte con los principales hallazgos:

- porcentaje de éxito por tarea,
- tiempo promedio de ejecución,
- principales puntos de fricción,
- nivel de satisfacción general,
- mejoras priorizadas según impacto.

Estos resultados servirán como ayuda directa para definir ajustes y mejoras en el **Sprint 3**, enfocándose en resolver los problemas de usabilidad detectados durante las pruebas.

---

# 4. Calidad del Software

## 4.1 Estándares de Código

El código sigue **PEP 8**, que es el estándar oficial de Python:

- **Variables y funciones:** `nombre_usuario`, `crear_paciente()` (minúsculas con guiones bajos)
- **Clases:** `LlamadaService`, `Notificacion` (primera letra de cada palabra en mayúscula)
- **Constantes:** `PLAN_FREEMIUM`, `ESTADO_CONFIRMADA` (todo en mayúsculas)
- **Archivos:** `llamada_service.py`, `models.py` (minúsculas con guiones bajos)

---

## 4.2 Herramientas utilizadas

**flake8** revisa que el código siga los estándares de estilo. **black** corrige automáticamente el formato. Se ejecutaron en todo el código nuevo de Sprint 2.

Resultado: 0 errores de estilo.

**bandit** revisa posibles problemas de seguridad (contraseñas escritas directamente en el código, configuraciones inseguras, etc.). Escaneó el código nuevo y reportó 0 problemas críticos ni medios.

---

# 5. Lo que Hicimos en Sprint 2

El cuidador ya puede usar Porvoz de punta a punta para recordatorios por llamadas  de voz. Lo principal que entregamos:

| Funcionalidad | Por qué es importante para el MVP |
|---------------|----------------------------------|
| Llamada automática con saludo personalizado (nombre + medicamento + instrucciones) | Es lo que hace distinto al producto: el paciente no abre nada, solo contesta el teléfono |
| Detección de respuestas ("sí", "no", "después", emergencia) | Sin esto no sabemos si el paciente tomó el medicamento y las alertas serían a ciegas |
| Reintentos configurables por medicamento | Un medicamento crítico puede tener más intentos que uno de rutina; cada caso es distinto |
| Alerta de emergencia con correo forzado | Si el paciente dice que se siente mal, el correo sale aunque el cuidador haya desactivado las notificaciones |
| Historial de llamadas con filtros | El cuidador (o el médico) puede ver semana a semana qué tomas se cumplieron y cuáles no |

Además de las funcionalidades principales:
- Dashboard mejorado con estadísticas de adherencia y últimas llamadas
- Formularios rediseñados para mejor navegación

**Historias implementadas**
- HU-04 — Llamadas automáticas con IA
- HU-05 — Registrar confirmación de toma
- HU-07 — Validación y manejo básico de errores
- HU-09 — Detectar respuestas negativas
- HU-11 — Dashboard básico de seguimiento
- HU-27 — Recuperar contraseña
- HU-29 — Historial de llamadas
- HU-30 — Sistema de notificaciones de emergencia
- HU-31 — Sistema de acciones post-llamada
- HU-32 — Integración de notificaciones con el correo
- HU-34 — Sistema responsive en celular


---

# 6. Qué Viene en Sprint 3

En Sprint 3 el foco principal es ejecutar las pruebas de usabilidad con los participantes del protocolo ya planeado, para probar mas casos de uso y mejorar nuestra funcionalidad principal. Se busca desplegar la aplicacion para probarla desde distintos dispositivos, y la posibilidad de cambiar notificaciones del correo a notificaciones de whatsapp segun lo pedido por los product owners.Además investigaremos sobre la implementacion para los distintos planes de pago de la aplicación. 

---

# 7. Evidencias de Ceremonias – Sprint 2


<table>
  <tr>
    <td><img src="pruebareunion14.png" width="300"/></td>
    <td><img src="pruebareunion15.png" width="300"/></td>
  </tr>
  <tr>
    <td><img src="pruebareunion16.png" width="300"/></td>
    <td><img src="pruebareunion17.png" width="300"/></td>
  </tr>
</table>

