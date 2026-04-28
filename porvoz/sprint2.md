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

Hay tres planes: **Básico** gratuito (1 paciente), **Familiar** (hasta 5) y **Profesional** (hasta 20).

**Propuesta de valor:** la llamada llega sola, sin que el paciente tenga que abrir la app o ver una notificación. El cuidador no necesita estar pendiente de cada toma: el sistema le avisa solo cuando algo sale mal.

---

## 1.4 Finanzas

### 1.4.1 Presupuesto Pre-Operación

**Horizonte:** 2 sprints (4 semanas). Somos un equipo de 4 personas; cada una recibe el salario mínimo legal vigente en Colombia 2024 (1.300.000/mes + 162.000 de auxilio de transporte = **1.462.000/mes**). Usamos nuestros propios equipos. Todos los valores en COP.

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
| Material digital básico (presentaciones, diseño) | unidad | 50.000 | 1 | 50.000 |
| **Subtotal Publicidad** | | | | **50.000** |
| | | | | |
| **TOTAL PRE-OPERACIÓN** | | | | **6.141.000** |

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

> Nota: se usa un número de EE.UU. en Twilio ($1.15/mes) en lugar de uno colombiano ($14/mes). Los pacientes lo pueden guardar en contactos; las llamadas salen igualmente desde "Porvoz". Gemini API es gratuito hasta ~7.500 clasificaciones/mes, que cubre todos los planes actuales; se reservan 10.000 COP como colchón para crecimiento. En etapa MVP el soporte lo asume el equipo fundador.

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
| **Historia de Usuario HU-04 – Llamadas automáticas** | | |
| Reintentos automáticos cuando el paciente dice que no | Unitaria | La lógica de reintento vive en `LlamadaService` sin depender de red; se prueba sola para verificar el conteo y la programación de la nueva llamada |
| El reintento no se crea si se superó el máximo configurado | Unitaria | Es la regla central de `max_reintentos` del medicamento; se prueba sola para confirmar que el sistema la respeta |
| No atender la llamada también genera un reintento | Unitaria | Verifica la rama `RESPUESTA_NO_ATENDIDA`, que debe disparar el mismo flujo que la negativa |
| **Historia de Usuario HU-05 – Registrar respuestas** | | |
| Detectar si el paciente dijo "sí" (confirmación) | Unitaria | El clasificador de palabras clave es una función determinística; no necesita llamadas reales para verificarse |
| Detectar si el paciente dijo "no" (negativa) | Unitaria | Misma razón; cubre también variaciones sin tilde ("ya lo tome") |
| Detectar si el paciente dijo "después" | Unitaria | Verifica variaciones coloquiales ("en un rato", "más tarde") |
| Filtrar mensajes que intenten manipular al modelo de IA | Unitaria | Prueba de seguridad: el mensaje se trunca y se limpian palabras de instrucción antes de enviarse |
| Validar que el número de teléfono tenga formato correcto | Unitaria | El validador cubre números colombianos con y sin código de país (+57) |
| **Historia de Usuario HU-06 – Alertas automáticas** | | |
| Confirmar la toma no genera alerta | Unitaria | Verifica que el flujo positivo no dispara alertas innecesarias |
| Respuesta negativa genera alerta de prioridad normal | Integración | Requiere modelos reales en base de datos (Llamada + RespuestaLlamada + Notificacion) para verificar la cadena completa |
| **Flujo completo entre componentes** | | |
| Paciente dice no → se reprograma la llamada → se crea alerta | Integración | Valida que los tres pasos de la cadena sucedan en orden con datos reales; es la prueba más importante de HU-04 y HU-06 juntas |
| El saludo de la llamada incluye nombre, medicamento e instrucciones | Integración | Verifica que el endpoint de voz arme correctamente el TwiML con los datos del paciente y el medicamento desde la base de datos |

Cada historia de usuario tiene al menos una prueba del **caso esperado (happy path)** y una del **caso alternativo o de error**, según los criterios de aceptación definidos en el backlog.

---

## 2.2 Tests Implementados

Los tests viven en los archivos del proyecto. El principal es `apps/llamadas/tests/test_services.py`, que cubre las reglas del servicio de llamadas (reintentos, clasificación de respuestas, alertas). Los 94 tests pasan en la suite completa y se ejecutan automáticamente en cada PR via GitHub Actions (ver sección 2.3).

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

[Insertar captura de la ejecución de los tests una vez se corra el comando]

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

Las pruebas están **planeadas en Sprint 2** y se ejecutarán en Sprint 3. El objetivo es detectar fricciones antes de cerrar el MVP, con cuidadores reales usando el sistema.

## 3.1 Participantes

- **Cantidad:** 8 personas
- **Perfil:** cuidadores reales (familiares o personal de salud), 25 a 65 años, nivel digital básico o medio
- **Exclusión:** personas con experiencia en desarrollo de software o UX
- **Reclutamiento:** red de contactos del equipo y aliados del piloto

## 3.2 Tareas

Las tareas se plantean como situaciones reales, no como instrucciones técnicas. El facilitador las lee en voz alta; el participante no sabe de antemano qué pasos seguir.

**T1 — Registrar un paciente nuevo**
*"Acabas de empezar a usar Porvoz. Tu mamá toma Losartán a las 8 a.m. y a las 8 p.m. Agrégala al sistema con ese medicamento."*

**T2 — Consultar una llamada que no fue contestada**
*"El sistema intentó llamar anoche y no hubo respuesta. Busca esa llamada y fíjate a qué hora fue y qué dice el resultado."*

**T3 — Entender una alerta activa**
*"Tienes una alerta nueva. Ábrela y cuéntame qué medicamento la generó y por qué."*

**T4 — Cambiar el horario de un medicamento**
*"Tu papá ahora toma el Metformín a las 7 a.m. en vez de las 8. Actualiza ese horario."*

**T5 — Agregar un segundo medicamento al mismo paciente**
*"Además del Losartán, tu mamá ahora también toma Atorvastatina todas las noches a las 9 p.m. Agrégalo."*

**T6 — Ver el historial de la semana**
*"Quieres saber cuántas llamadas contestó tu paciente esta semana. Encuéntralo."*

**T7 — Actualizar el teléfono del paciente**
*"Tu mamá cambió de número. El nuevo es 300 111 2233. Actualízalo para que las llamadas lleguen ahí."*

**T8 — Cerrar sesión y volver a entrar**
*"Sal de la aplicación y vuelve a entrar. Confirma que el paciente y el medicamento que registraste antes siguen ahí."*

**Criterio de éxito por tarea:** completada sin intervención del facilitador.

---

## 3.3 Hipótesis

Las hipótesis nacen de decisiones de diseño concretas tomadas en Sprint 1 y Sprint 2: formularios de varios pasos, navegación por menú lateral, alertas como lista de eventos.

- **H1:** El formulario de registro (paciente + medicamento en dos pasos separados) causará que al menos 3 de 8 participantes no terminen T1 en menos de 4 minutos. El diseño actual no agrupa los dos pasos en un solo flujo visible.
- **H2:** La sección de historial de llamadas será el punto con más errores de navegación (T2 y T6), porque no hay acceso directo desde el dashboard y requiere ir al perfil del paciente primero.
- **H3:** La opción para editar teléfono y horario (T4 y T7) no es visible a primera vista; está dentro de la ficha del paciente, sin un botón de acceso rápido en la lista.

## 3.4 Preguntas de Investigación

Las preguntas están alineadas a las tareas y a las hipótesis anteriores:

1. ¿Qué porcentaje de participantes completa cada tarea sin ayuda? *(mide directamente H1, H2 y H3)*
2. ¿En qué paso específico de T1 se demoran o confunden más? *(valida H1)*
3. ¿Cuántos intentos necesitan para llegar al historial de llamadas desde la pantalla principal? *(valida H2)*
4. ¿Qué textos o botones generan más preguntas en voz alta durante la sesión?
5. ¿Qué mejora pediría el participante si pudiera cambiar una sola cosa?

## 3.5 Criterios de Evaluación

| Métrica | Cómo se mide | Meta |
|---------|--------------|------|
| Tasa de éxito por tarea | % de participantes que terminan sin que el facilitador intervenga | ≥ 75% por tarea |
| Tiempo por tarea | El observador cronometra desde que se lee la tarea hasta que el participante dice "listo" | T1 ≤ 4 min / T2–T8 ≤ 3 min |
| Errores de navegación | Número de veces que el participante abre una sección que no lleva al objetivo | ≤ 2 por tarea |
| Satisfacción general | Encuesta Likert 1–5 al final de la sesión | ≥ 3.5 / 5 |
| Tasa de abandono | % de participantes que piden ayuda o se rinden antes de terminar | ≤ 25% por tarea |

## 3.6 Materiales

- Consentimiento informado (1 hoja, firmado antes de empezar)
- Hoja de tareas (T1 a T8, una por página para evitar que el participante lea lo que sigue)
- Plantilla de observación (tiempo, errores, resultado y comentarios libres por tarea)
- Encuesta de satisfacción Likert 1–5 (5 preguntas, al final)
- Guía de cierre con 3 preguntas abiertas: qué les gustó, qué cambiarían, qué les confundió más

## 3.7 Cómo se conduce la sesión

**Duración:** 40 a 45 minutos por participante.

| Bloque | Tiempo | Qué pasa |
|--------|--------|----------|
| Introducción | 5 min | Se explica el objetivo, se firma el consentimiento |
| Exploración libre | 5 min | El participante navega sin tareas; el facilitador observa sin guiar |
| Tareas T1–T8 | 25 min | Cada tarea se lee en voz alta; sin pistas; se cronometra |
| Encuesta | 5 min | Likert 1–5 de forma individual y en silencio |
| Cierre | 5 min | 3 preguntas abiertas en conversación |

**Roles:**
- **Facilitador:** lee las tareas, maneja el tiempo, no da pistas.
- **Observador:** registra errores, tiempos y comentarios textuales del participante.
- **Analista:** consolida resultados después de las 8 sesiones.

## 3.8 Qué se hace con los resultados

Al terminar las 8 sesiones el analista prepara un reporte con: tasa de éxito y tiempo promedio por tarea, los 3 puntos de mayor fricción, puntaje de satisfacción y lista de mejoras priorizadas. Ese reporte entra directo al backlog de Sprint 3.

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

El cuidador ya puede usar Porvoz de punta a punta para recordatorios por voz. Lo principal que entregamos:

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

**Historias implementadas (resumen breve):**
- HU-32 — Integración de notificaciones con el correo
- HU-27 — Recuperar contraseña
- HU-30 — Sistema de notificaciones de emergencia
- HU-11 — Dashboard básico de seguimiento
- HU-29 — Historial de llamadas
- HU-31 — Sistema de acciones post-llamada
- HU-04 — Llamadas automáticas con IA
- HU-05 — Registrar confirmación de toma
- HU-09 — Detectar respuestas negativas

**Bugs corregidos:**

| Bug | Severidad | Corrección |
|-----|-----------|------------|
| Los reintentos no se creaban por un error en la condición de comparación | Crítico | Corregido en el servicio de llamadas |
| Las instrucciones del medicamento no se escuchaban en la llamada | Alto | Se agregó el parámetro que faltaba al iniciar la llamada |
| No había enlace desde el perfil del paciente al historial de llamadas | Alto | Se agregó el botón en la vista de detalle del paciente |
| Las tarjetas de medicamento eran muy angostas en pantallas pequeñas | Bajo | Se ajustó el CSS |

**Métricas del sprint:**
- 11 historias completadas, 89 puntos entregados
- 84% de cobertura de tests, 94 pruebas automáticas pasando
- 0 vulnerabilidades de seguridad
- 34 commits, 6 pull requests mergeadas

---

# 6. Qué Viene en Sprint 3

En Sprint 3 el foco principal es ejecutar las pruebas de usabilidad con los participantes del protocolo ya planeado, agregar un panel general que muestre el estado de todos los pacientes en una sola vista y permitir exportar reportes de adherencia. Si el tiempo lo permite, se explorará también el inicio de sesión con Google para simplificar el acceso y alertas por SMS como canal adicional para emergencias.

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

