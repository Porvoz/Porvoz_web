# Sprint 3 – Porvoz: Despliegue y Pruebas Finales

---

# 1. Caso de Negocio – Tercera Versión (Final)

## 1.1 Actualización Ejecutiva

Con los resultados de Sprint 2 validados (102 tests pasando, MVP funcional), Sprint 3 enfoca la viabilidad técnica y operativa del proyecto para producción. Las pruebas de usabilidad con 8 cuidadores reales permiten ajustar la interfaz, el despliegue en nube garantiza accesibilidad global, y el manual completo prepara el sistema para entrega a clientes.

**Estado:** En validación de usuarios reales | Despliegue listo para QA | MVP optimizado según feedback

---

## 1.2 Sección 6 — Viabilidad del Proyecto

### 1.2.1 Análisis de Viabilidad Técnica

#### ¿Es técnicamente viable?

| Criterio | Evaluación | Evidencia |
|----------|-----------|----------|
| Arquitectura de microservicios | Viable | Django + Celery + Twilio integrados; webhook de llamadas validado en Sprint 2 |
| Base de datos | Viable | PostgreSQL en producción soporta hasta 100M registros; schema optimizado para queries de historial |
| Escalabilidad de llamadas | Viable | Twilio maneja 1M+ llamadas/día; limite actual es ~15k/día por plan (Profesional) |
| Despliegue en nube | Viable | Docker + Kubernetes o PaaS (Heroku, Railway); CI/CD con GitHub Actions implementado |
| Seguridad en datos de salud | Viable con restricciones | HIPAA requiere auditoría legal previa; cumple GDPR con cifrado en tránsito y almacenamiento |

**Conclusión técnica:** El sistema es escalable y seguro. Los riesgos técnicos identificados en Sprint 2 (R1, R5, R10) tienen mitigaciones implementadas.

---

### 1.2.2 Análisis de Viabilidad Operativa

#### ¿Podemos operarlo y mantenerlo?

| Criterio | Evaluación | Plan |
|----------|-----------|------|
| Equipo mínimo de operación | Viable | 1 DevOps + 1 Backend (escalas a 2 cuando > 500 clientes) |
| SLA y monitoreo | Viable | Datadog o New Relic; SLA 99.5% en contrato; alertas en Slack |
| Recuperación ante fallos | Viable | Backups diarios en S3; DR plan en región alternativa (< 4h RTO) |
| Mantenimiento de Twilio | Viable | Contrato directo; soporte 24/7; cambio de proveedor posible (Vonage, bandwidth.com) |
| Cumplimiento normativo | Requiere validación | Revisar con abogado antes de producción; notificaciones de emergencia pueden tener requisitos especiales |

**Conclusión operativa:** Es viable operativamente con un equipo pequeño. El riesgo legal (R2, R9) debe validarse antes del lanzamiento.

---

### 1.2.3 Análisis de Viabilidad de Mercado

#### ¿Hay demanda real?

| Indicador | Datos | Conclusión |
|-----------|-------|-----------|
| Problema identificado | 50% de pacientes no cumplen medicamentos (OMS) | Problema real, validado |
| Segmento target | 5.7M+ mayores de 65 en Colombia | Mercado grande |
| Validación con usuarios | Protocolo planeado; pruebas a ejecutar Sprint 3 | En curso |
| Competencia | Doctoclick, Tele.md, apps genéricas | Diferenciador claro (voz + IA) |
| Disposición a pagar | Encuesta informal a 3 clínicas: "pagarían $60k–$150k/mes" | Promisorio |

**Conclusión de mercado:** Viabilidad de mercado depende de resultados de pruebas de usabilidad (Sprint 3).

---

### 1.2.4 Análisis Costo-Beneficio

#### Escenario base (conservador) — año 1

| Item | Valor | Observación |
|------|-------|-------------|
| Ingresos (8 Familiar + 2 Profesional) | $3.948.000/año | 479.600 × 12; margen mensual ya descontado costo variable |
| Costos operativos fijos | $3.355.200/año | 279.600 × 12 |
| Beneficio neto (año 1) | +$592.800 | Operación rentable desde mes 2; inversión inicial (~$6M) recuperable en año 1+ con más clientes |
| Break-even estimado | Mes 6–8 | Si 15+ clientes firmados en Q2 2026 |

**Conclusión costo-beneficio:** Viable si se valida demanda (Sprint 3 y Q2) y se capturan 4+ clientes pagos antes del Q3.

---

### 1.2.5 Resumen de Viabilidad General

| Dimensión | Resultado | Riesgo |
|-----------|-----------|--------|
| Técnica | Viable | Bajo |
| Operativa | Viable | Bajo-Moderado (requiere DevOps) |
| Mercado | Validando | Moderado (depende de usabilidad) |
| Financiera | Viable | Moderado (tiempo a break-even) |
| Normativa | Revisar | Moderado-Alto (antes de producción) |

**Recomendación:** Procedimiento a Sprint 3 y despliegue piloto. Paralelo: consultar con abogado sobre HIPAA y permisos de telecomunicaciones.

---

## 1.3 Conclusión del Caso de Negocio

Porvoz es **técnicamente viable, operativamente escalable y financieramente rentable** si se valida la demanda de usuarios reales en Sprint 3. 

**Condiciones de lanzamiento:**
1. Pruebas de usabilidad exitosas (≥75% tasa de éxito en tareas)
2. Despliegue estable en producción (AWS o similar)
3. Aprobación legal de normativa de salud (pre-lanzamiento)
4. Mínimo 2 clientes piloto comprometidos (Q2 2026)

**Conclusión:** Proyecto **APROBADO PARA PRODUCCIÓN** tras validación legal y usabilidad. Impacto esperado: 50% de adherencia medicamentosa en pacientes registrados, reducción de hospitalizaciones evitables, margen operativo positivo en mes 6.

---

---

# 2. Resultados de Pruebas de Usabilidad

Las pruebas de usabilidad se ejecutan en Sprint 3 con 8 cuidadores reales siguiendo el protocolo definido en Sprint 2. Esta sección documenta el proceso, resultados y ajustes posteriores.

## 2.1 Metodología

**Laboratorio:** Laboratorio de investigación EAFIT  
**Herramienta:** Eye tracker fijo (opcional)  
**Participantes:** 8 cuidadores reales (edad 25-65, sin experiencia en UX/desarrollo)  
**Aplicación testada:** Porvoz - Sistema de recordatorios de medicamentos  
**Duración por sesión:** 10-15 minutos

---

## 2.2 Hipótesis y Resultados

### HIPOTESIS #1 - Registrar Paciente

El usuario agenda un nuevo paciente con eficacia y eficiencia.

**Tarea:**
"Acabas de empezar a usar Porvoz. Tu mamá toma Losartán a las 8 a.m. y a las 8 p.m. Agrégala al sistema con ese medicamento."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- 6 de 8 usuarios completan la tarea en un rango de 2 a 4 minutos

**Resultados:**

| Usuario | Logró efectivamente | Tiempo (min) | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #2 - Consultar Llamada No Contestada

El usuario encuentra y consulta llamadas no contestadas con eficacia.

**Tarea:**
"El sistema intentó llamar anoche y no hubo respuesta. Busca esa llamada y fíjate a qué hora fue y qué dice el resultado."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- 6 de 8 usuarios completan la tarea en menos de 2 minutos

**Resultados:**

| Usuario | Logró efectivamente | Tiempo (min) | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #3 - Entender Alerta Activa

El usuario comprende adecuadamente las alertas sin necesidad de ayuda externa.

**Tarea:**
"Tienes una alerta nueva. Ábrela y cuéntame qué medicamento la generó y por qué."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- Los usuarios pueden explicar la causa de la alerta sin intervención

**Resultados:**

| Usuario | Logró efectivamente | Explicación clara | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #4 - Cambiar Horario Medicamento

El usuario edita horarios de medicamentos de forma intuitiva.

**Tarea:**
"Tu papá ahora toma el Metformín a las 7 a.m. en vez de las 8. Actualiza ese horario."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- 6 de 8 usuarios encuentran la opción de edición en menos de 1 minuto

**Resultados:**

| Usuario | Logró efectivamente | Tiempo (min) | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #5 - Agregar Segundo Medicamento

El usuario agrega múltiples medicamentos a un mismo paciente sin confusión.

**Tarea:**
"Además del Losartán, tu mamá ahora también toma Atorvastatina todas las noches a las 9 p.m. Agrégalo."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- 6 de 8 usuarios completan en menos de 2 minutos

**Resultados:**

| Usuario | Logró efectivamente | Tiempo (min) | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #6 - Ver Historial de la Semana

El usuario consulta el historial de llamadas semanalmente con claridad.

**Tarea:**
"Quieres saber cuántas llamadas contestó tu paciente esta semana. Encuéntralo."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- Los usuarios pueden identificar llamadas confirmadas vs. negadas

**Resultados:**

| Usuario | Logró efectivamente | Identificó correctamente | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #7 - Actualizar Teléfono del Paciente

El usuario actualiza el número telefónico del paciente fácilmente.

**Tarea:**
"Tu mamá cambió de número. El nuevo es 300 111 2233. Actualízalo para que las llamadas lleguen ahí."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- 6 de 8 usuarios encuentran la opción en menos de 1 minuto

**Resultados:**

| Usuario | Logró efectivamente | Tiempo (min) | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

### HIPOTESIS #8 - Persistencia de Datos

El usuario verifica que los datos se mantienen después de logout/login.

**Tarea:**
"Sal de la aplicación y vuelve a entrar. Confirma que el paciente y el medicamento que registraste antes siguen ahí."

**Criterios de validación:**
- Completan correctamente la tarea 6 de 8 usuarios (75%)
- Los datos registrados permanecen intactos después de reingreso

**Resultados:**

| Usuario | Logró efectivamente | Datos persistieron | Observaciones |
|---------|---|---|---|
| Usuario 1 | | | COMPLETA ESTE CAMPO |
| Usuario 2 | | | COMPLETA ESTE CAMPO |
| Usuario 3 | | | COMPLETA ESTE CAMPO |
| Usuario 4 | | | COMPLETA ESTE CAMPO |
| Usuario 5 | | | COMPLETA ESTE CAMPO |
| Usuario 6 | | | COMPLETA ESTE CAMPO |
| Usuario 7 | | | COMPLETA ESTE CAMPO |
| Usuario 8 | | | COMPLETA ESTE CAMPO |

**Principales Hallazgos:**

COMPLETA ESTE CAMPO

**Conclusiones:**

COMPLETA ESTE CAMPO

**Validación:** HIPOTESIS VALIDADA / NO VALIDADA (completar tras analizar datos)

---

## 2.3 Satisfacción General

**Criterios de validación:**
- Puntuación SUS (System Usability Scale) mayor o igual a 68%
- Tasa de recomendación a otros cuidadores mayor a 75%
- Tasa de abandono menor a 25%

**Resultados:**

| Usuario | Satisfacción SUS (%) | Recomendaría | Observaciones |
|---------|---|---|---|
| Usuario 1 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 2 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 3 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 4 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 5 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 6 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 7 | | Sí/No | COMPLETA ESTE CAMPO |
| Usuario 8 | | Sí/No | COMPLETA ESTE CAMPO |
| **PROMEDIO** | **— %** | **— %** | **Meta ≥68% / ≥75%** |

---

## 2.4 Ajustes a Interfaz (Post-Usabilidad)

### 2.4.1 Cambios Menores (Implementables en Sprint 3)

| ID | Ajuste | Complejidad | Responsable | Estado |
|----|--------|-------------|-------------|--------|
| ADJ-01 | COMPLETA ESTE CAMPO | Baja/Media | — | Pendiente |
| ADJ-02 | COMPLETA ESTE CAMPO | Baja/Media | — | Pendiente |

---

### 2.4.2 Cambios Complejos (Sprint 4)

| ID | Ajuste | Justificación | Estimación |
|----|--------|---------------|-----------|
| ADJ-C1 | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO | — puntos |
| ADJ-C2 | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO | — puntos |

---

## 2.5 Conclusión de Usabilidad

**Status:** Ejecución en progreso.

Una vez completadas las 8 sesiones y consolidados los resultados:
- Se aplicarán ajustes menores antes de despliegue final.
- Se documentarán ajustes complejos como historias para Sprint 4 (si aplica).
- Se generará reporte ejecutivo para Product Owner.

---

---

# 3. Manual de Usuario

## 3.1 Descripción para Usuarios Finales

Porvoz incluye una guía de uso integrada en la aplicación para cuidadores. El manual cubre:

- Cómo crear una cuenta e iniciar sesión
- Registrar un nuevo paciente con todos sus datos
- Agregar medicamentos con horarios e instrucciones especiales
- Consultar el historial de llamadas realizadas
- Entender y responder a alertas de incumplimiento
- Cambiar configuración de notificaciones (email, preferencias)
- Preguntas frecuentes y contacto de soporte

La interfaz incluye **tooltips en cada campo** y una sección de **ayuda contextual** para que los usuarios no requieran documentación externa. Todos los formularios tienen **validaciones claras** que indican qué datos son requeridos y en qué formato.

Objetivo: que cualquier cuidador sin experiencia técnica pueda usar el sistema sin dificultades.

---

## 3.2 Documentación para Product Owners

Para revisión, aprobación y distribución a clientes, se entrega un **manual técnico completo en PDF** con:

- Introducción y misión de Porvoz
- Guía paso a paso de cada funcionalidad
- Capturas de pantalla de todas las pantallas principales
- Casos de uso reales (ejemplos de cómo usar)
- FAQ con respuestas detalladas
- Información de soporte y contacto

**Documento:** [Manual_Porvoz_v1.0.pdf](COMPLETA ESTE CAMPO - agregar link al PDF una vez esté listo)

**Responsable de elaboración:** COMPLETA ESTE CAMPO  
**Fecha de entrega esperada:** COMPLETA ESTE CAMPO  
**Ubicación en repositorio:** /docs/manual/ o Drive compartido

---

## 3.3 Contenido del Manual (Estructura)

| Sección | Responsable | Estado |
|---------|-----------|--------|
| Portada y tabla de contenidos | COMPLETA ESTE CAMPO | Pendiente |
| Introducción a Porvoz | COMPLETA ESTE CAMPO | Pendiente |
| Guía: Crear cuenta e iniciar sesión | COMPLETA ESTE CAMPO | Pendiente |
| Guía: Registrar paciente | COMPLETA ESTE CAMPO | Pendiente |
| Guía: Agregar medicamentos | COMPLETA ESTE CAMPO | Pendiente |
| Guía: Consultar historial de llamadas | COMPLETA ESTE CAMPO | Pendiente |
| Guía: Alertas y notificaciones | COMPLETA ESTE CAMPO | Pendiente |
| Configuración de perfil | COMPLETA ESTE CAMPO | Pendiente |
| FAQ y troubleshooting | COMPLETA ESTE CAMPO | Pendiente |
| Información de soporte | COMPLETA ESTE CAMPO | Pendiente |

---

## 3.4 Formatos de Entrega

**Para usuarios en la aplicación:**
- Tooltips emergentes en campos del formulario
- Sección "Ayuda" en el menú lateral
- Links a documentación para cada pantalla principal

**Para Product Owners y clientes:**
- PDF descargable e imprimible
- Versión web (sitio estático) con búsqueda
- Videos cortos (opcional): demostración de 2-3 min por funcionalidad

**Status:** Pendiente elaboración post-usabilidad. Los ajustes de interfaz derivados de las pruebas de usabilidad se incorporarán antes de finalizar el manual.

---

---

# 4. Despliegue de la Aplicación

## 4.1 Infraestructura y Plan de Despliegue

### 4.1.1 Plataforma Seleccionada

| Opción | Evaluación | Decisión |
|--------|-----------|----------|
| AWS EC2 + RDS + CloudFront | ✅ Completo, control total | ⏳ Por evaluar |
| Heroku | ✅ Fácil, escalable | ⏳ Por evaluar |
| Railway.app | ✅ Moderno, Git-nativo | ⏳ Por evaluar |
| Digital Ocean App Platform | ✅ Económico, documentado | ⏳ Por evaluar |

**Recomendación:** Railway.app (simplicidad) o AWS (escalabilidad futura). Decisión final por Product Owner.

---

### 4.1.2 Componentes de Infraestructura

```
┌─────────────────────────────────────────────────────────┐
│ Internet / Dominio (porvoz.com)                        │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  CloudFront / CDN   │  (cacheo estático)
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼──┐  ┌───────▼────────┐  ┌──▼────┐
│  SSL │  │ Django + Gunicorn │  │ Redis  │
│      │  │   (web service)    │  │(cache) │
└───┬──┘  └───────┬────────┘  └──┬────┘
    │             │              │
    └─────────────┼──────────────┘
                  │
           ┌──────▼──────┐
           │  PostgreSQL │
           │  (RDS/prod) │
           └─────────────┘
                  │
    ┌─────────────┴──────────┐
    │                        │
┌───▼────┐        ┌──────────▼─────┐
│ Twilio │        │ Google Gemini  │
│ (calls)│        │ (IA classifier)│
└────────┘        └────────────────┘
```

---

### 4.1.3 Configuración Base

| Componente | Configuración | Status |
|-----------|--------------|--------|
| **Python** | 3.11 en producción | ⏳ |
| **Django** | 4.2 LTS | ⏳ |
| **Base de datos** | PostgreSQL 14+ (prod), SQLite (dev) | ⏳ |
| **Web server** | Gunicorn + Nginx | ⏳ |
| **Variables de entorno** | `.env` con secrets (no versionado) | ⏳ |
| **SSL/TLS** | Let's Encrypt, auto-renovación | ⏳ |
| **Logs** | Consolidados en Datadog o CloudWatch | ⏳ |
| **Backups** | Diarios a S3, retenidos 30 días | ⏳ |

---

## 4.2 Proceso de Despliegue

### 4.2.1 Pre-Despliegue (Checklist)

- Todos los tests pasan (`python manage.py test`)
- Zero vulnerabilidades críticas (`bandit`, `safety`)
- `.env.example` actualizado
- Migraciones en orden (`makemigrations`, `migrate`)
- `SECRET_KEY` único en producción
- `DEBUG = False` en settings/production.py
- Base de datos de producción respalda

---

### 4.2.2 Pasos de Despliegue (Manual)

**Opción 1: AWS EC2 (Manual)**

```bash
# 1. Conectar a instancia
ssh -i key.pem ec2-user@IP_PUBLICA

# 2. Clonar repositorio
git clone https://github.com/Porvoz/Porvoz_web.git
cd Porvoz_web/porvoz

# 3. Crear venv e instalar dependencias
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 4. Variables de entorno
cp ../.env.example .env
# Editar .env con valores de producción (DB, Twilio, Gemini, etc.)

# 5. Migraciones
python manage.py migrate --database=production

# 6. Recolectar estáticos
python manage.py collectstatic --noinput

# 7. Iniciar servicios
gunicorn config.wsgi:application --bind 0.0.0.0:8000
# En producción: usar systemd o supervisor

# 8. Configurar Nginx como proxy reverso
# Crear /etc/nginx/sites-available/porvoz (ver config más abajo)
```

---

**Opción 2: Railway.app (Automático desde Git)**

```yaml
# railway.json en la raíz del repo
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "python porvoz/manage.py migrate && gunicorn config.wsgi"
  }
}
```

Luego:
1. Conectar repositorio GitHub a Railway
2. Railway detecta `railway.json`
3. Cada push a `main` dispara despliegue automático

---

### 4.2.3 Configuración de Nginx (Proxy Reverso)

```nginx
# /etc/nginx/sites-available/porvoz

upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name porvoz.com www.porvoz.com;

    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name porvoz.com www.porvoz.com;

    ssl_certificate /etc/letsencrypt/live/porvoz.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/porvoz.com/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/ubuntu/Porvoz_web/porvoz/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Porvoz_web/porvoz/media/;
    }
}
```

---

## 4.3 Pruebas Post-Despliegue

### 4.3.1 Checklist de QA

| Test | Comando / Paso | Expected | Status |
|------|---|---|---|
| Acceso a la web | Abrir `porvoz.com` | Carga en < 2s | Pendiente |
| Login funciona | Ingresar credenciales | Redirección a dashboard | Pendiente |
| Crear paciente | Enviar formulario | Paciente guardado en BD | Pendiente |
| Llamada test | Twilio test call | Responde con saludo | Pendiente |
| Webhook callbackrecibe respuesta | Curl a `/webhook/respuesta` | Status 200, BD actualizada | Pendiente |
| Email notificación | Generar alerta | Correo en inbox | Pendiente |
| Historial visible | Ver historial paciente | Llamadas listadas, filtros funcionan | Pendiente |
| SSL válido | `curl -I https://porvoz.com` | HTTP 200, certificado válido | Pendiente |
| Logs accesibles | `journalctl -u gunicorn` | Logs de request/error visibles | Pendiente |

---

### 4.3.2 Pruebas de Carga

```bash
# Simular 100 usuarios simultáneos durante 5 min
ab -n 10000 -c 100 https://porvoz.com/

# Resultado esperado:
# - Requests per second: > 50
# - Failed requests: 0
# - Average response time: < 500ms
```

---

## 4.4 Monitoreo y Mantenimiento

### 4.4.1 Herramientas de Monitoreo

| Herramienta | Métrica | Alert Threshold |
|-------------|---------|-----------------|
| Datadog / New Relic | CPU, memoria, disco | > 80% |
| CloudWatch (AWS) | Errores HTTP 5xx | > 1% de requests |
| Sentry | Excepciones Python | Cualquier error crítico |
| Uptime Robot | Disponibilidad web | Downtime > 5 min |

---

### 4.4.2 Plan de Backups

| Dato | Frecuencia | Destino | Retención |
|------|-----------|---------|-----------|
| Base de datos | Diaria (2 a.m.) | S3 + Glacier | 30 días |
| Archivos media | Diaria | S3 | 30 días |
| Logs | Semanal | CloudWatch + S3 | 90 días |

**Prueba de recuperación:** Mensualmente simular restauración desde backup.

---

## 4.5 Documentación de Despliegue

### 4.5.1 README de Despliegue

**Archivo:** `DEPLOYMENT.md`

```markdown
# Despliegue de Porvoz

## Prerequisitos
- Cuenta en AWS / Railway / similar
- Dominio configurado (DNS)
- Secretos: Twilio API Key, Gemini API, SMTP password

## Despliegue en AWS (Manual)
[Instrucciones paso a paso...]

## Despliegue en Railway (Automático)
[Instrucciones...]

## Rollback
Si algo sale mal, revertir a commit anterior:
\`\`\`
git revert <COMMIT>
git push origin main  # dispara redeploy automático
\`\`\`
```

---

### 4.5.2 Link a la Aplicación

**URL de Producción:** [Insertar URL en README.md]

```markdown
## 🚀 Aplicación en Producción

Acceder aquí: https://porvoz.com
```

---

## 4.6 Status General de Despliegue

| Fase | Status | Fecha Esperada |
|------|--------|---|
| Configurar infraestructura | Pendiente | Semana 1 Sprint 3 |
| Pre-despliegue checklist | Pendiente | Semana 1 Sprint 3 |
| Despliegue a staging | Pendiente | Semana 2 Sprint 3 |
| Tests de carga | Pendiente | Semana 2 Sprint 3 |
| Despliegue a producción | Pendiente | Semana 3 Sprint 3 |

---

---

# 5. Desarrollo Producto Final (Sprint 3)

## 5.1 Funcionalidades Nuevas Planeadas

Las siguientes funcionalidades se planean para Sprint 3 basadas en feedback de Sprint 2 y requisitos del PO.

### 5.1.1 Dashboard Mejorado (Multi-Pacientes)

**Historia:** HU-35 — Panel general de todos los pacientes en una vista

**Descripción:** El cuidador ve un resumen de TODOS sus pacientes en una sola pantalla: últimas llamadas, alertas activas, adherencia general.

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Vista tabla/grid | Listar todos los pacientes con columnas: nombre, última toma, próximo medicamento, estado | Pendiente |
| Gráfico de adherencia | Barras/lineas de adherencia por paciente (últimos 7 días) | Pendiente |
| Alertas consolidadas | Mostrar alertas activas de TODOS los pacientes en un solo feed | Pendiente |
| Estadísticas globales | Total de tomas confirmadas/negadas esta semana, tasa de adherencia general | Pendiente |

**Tests esperados:** 4–5

---

### 5.1.2 Exportar Reportes de Adherencia

**Historia:** HU-36 — Exportar reporte de adherencia en PDF/CSV

**Descripción:** El cuidador puede descargar un reporte con todas las tomas de un paciente en un rango de fechas, útil para llevar al médico.

| Formato | Contenido | Status |
|---------|-----------|--------|
| **PDF** | Tabla legible, gráficos de adherencia, observaciones | Pendiente |
| **CSV** | Datos brutos para análisis en Excel | Pendiente |

**Endpoint:** `GET /api/pacientes/{id}/reportes/descargar?formato=pdf&fecha_inicio=2026-05-01&fecha_fin=2026-05-31`

**Tests esperados:** 2–3

---

### 5.1.3 Notificaciones por WhatsApp (Opcional)

**Historia:** HU-37 — Enviar alertas también por WhatsApp (además de email)

**Descripción:** Opcionalmente, el cuidador puede recibir alertas en WhatsApp en lugar de (o además de) correo.

**Servicios requeridos:**
- Twilio WhatsApp API (activar en cuenta)
- Número de WhatsApp Business de Porvoz

**Status:** Depende de feedback del PO y disponibilidad de APIs

**Tests esperados:** 2

---

### 5.1.4 Investigación: Sistema de Planes de Pago

**Historia:** HO-40 — Modelo de Negocio y Estrategia de Monetización

**Descripción:** Investigación sobre cómo implementar los 3 planes (Básico, Familiar, Profesional) en la aplicación.

**Preguntas a responder:**

- ¿Qué cambios en modelo de datos se requieren para diferenciar planes?
- ¿Cómo enforcar límites de pacientes y llamadas por plan?
- ¿Integración con Stripe, Wompi o MercadoPago?
- ¿Cómo manejar transiciones entre planes?
- ¿Qué métricas de rentabilidad deben monitorearse?
- ¿Estrategia de precios competitiva vs. sostenibilidad operativa?

**Entregable:** Documento de diseño técnico de sistema de pagos + análisis de viabilidad.

**Status:** Documentación en Progreso

---

## 5.2 Funcionalidades de Seguridad, Integridad y Compliance

### 5.2.1 Validación de Usuarios

**Historia:** HU-39 — Validación de usuarios

**Descripción:** Implementar validación robusta de datos de usuario en registro y login: emails únicos, contraseñas fuertes, verificación por correo.

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Email único | Prevenir registros duplicados | Pendiente |
| Contraseña fuerte | Requerir mínimo 8 caracteres, mayúsculas, números | Pendiente |
| Verificación email | Enviar correo de confirmación antes de activar cuenta | Pendiente |
| Rate limiting | Limitar intentos de login fallidos | Pendiente |

**Tests esperados:** 4–5

---

### 5.2.2 Pruebas y Medidas de Seguridad

**Historia:** HU-47 — Pruebas y medidas de seguridad e integridad de la webapp

**Descripción:** Ejecutar suite completa de pruebas de seguridad y documentar hallazgos.

| Tipo de Prueba | Descripción | Status |
|---|---|---|
| OWASP Top 10 | Verificar contra inyección, XSS, CSRF, etc. | Pendiente |
| SQL Injection | Probar parametrización de queries | Pendiente |
| XSS (Cross-Site Scripting) | Verificar sanitización de inputs | Pendiente |
| CSRF Tokens | Validar protección en formularios | Pendiente |
| Autenticación y Sesiones | Probar timeout, revocación de tokens | Pendiente |
| Encriptación | Verificar TLS/SSL, cifrado de datos sensibles | Pendiente |

**Entregable:** Reporte de seguridad con recomendaciones y status de cada hallazgo.

**Tests esperados:** 8–10

---

### 5.2.3 Compliance y Aspectos Legales en Salud

**Historia:** HU-33 — Compliance y Aspectos Legales en Salud

**Descripción:** Validación de cumplimiento normativo de datos de salud según HIPAA, GDPR, normativa colombiana.

| Requisito | Descripción | Status |
|-----------|-----------|--------|
| Cifrado de datos | PII en tránsito y en reposo | Pendiente |
| Consentimiento | Términos y privacidad aceptados por usuario | Pendiente |
| Auditoría | Log de accesos a datos de salud | Pendiente |
| Retención | Política de eliminación de datos (GDPR right to be forgotten) | Pendiente |
| Documentación legal | Términos de servicio, política de privacidad | Pendiente |

**Entregable:** Documento de Compliance + Checklist de conformidad.

**Status:** Requiere revisión con abogado especializado.

---

## 5.3 Funcionalidades de Administración y Soporte

### 5.3.1 Panel de Administración — Gestión de Pagos

**Historia:** HU-50 — Panel de Administración — Gestión de Pagos

**Descripción:** Superadmin puede ver y gestionar pagos, planes, suscripciones de usuarios.

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Dashboard financiero | Ingresos, número de clientes activos, MRR (Monthly Recurring Revenue) | Pendiente |
| Gestión de suscripciones | Cancelar, cambiar plan, reactivar cuentas | Pendiente |
| Historial de transacciones | Log de pagos realizados y fallidos | Pendiente |
| Facturación | Generar facturas por período | Pendiente |

**Tests esperados:** 4–5

---

### 5.3.2 Historial de Transacciones

**Historia:** HU-51 — Historial de Transacciones

**Descripción:** Usuarios pueden ver su historial completo de transacciones, estados de pago, facturas.

| Función | Descripción | Status |
|---------|-----------|--------|
| Vista de transacciones | Listar pagos, fechas, montos, estado | Pendiente |
| Descargar factura | Generar PDF de factura | Pendiente |
| Filtrar por período | Buscar transacciones en rango de fechas | Pendiente |
| Estados de pago | Mostrar si está pendiente, pagado, fallido, reembolsado | Pendiente |

**Tests esperados:** 3

---

### 5.3.3 Códigos de Acceso a Planes

**Historia:** HU-52 — Códigos de Acceso a Planes

**Descripción:** Superadmin puede generar códigos de acceso (tokens, cupones) para activar planes.

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Generar códigos | Crear códigos únicos con límite de usos | Pendiente |
| Validar códigos | Verificar que código es válido al activarlo | Pendiente |
| Límite de usos | Controlar cuántas veces se puede usar un código | Pendiente |
| Vencimiento | Códigos pueden expirar si no se usan en X días | Pendiente |

**Tests esperados:** 4

---

### 5.3.4 Sistema de Tickets de Soporte

**Historia:** HU-53 — Sistema de Tickets de Soporte

**Descripción:** Los usuarios pueden crear tickets de soporte y seguir el estado de sus solicitudes.

| Función | Descripción | Status |
|---------|-----------|--------|
| Crear ticket | Formulario para reportar problemas/preguntas | Pendiente |
| Estados | Abierto, en progreso, resuelto, cerrado | Pendiente |
| Comentarios | Usuario y admin pueden comentar en el ticket | Pendiente |
| Asignación | Admin asigna tickets a staff de soporte | Pendiente |
| Notificaciones | Email cuando se actualiza estado del ticket | Pendiente |

**Tests esperados:** 5

---

### 5.3.5 Gestión de Usuarios como Superadmin

**Historia:** HU-54 — Gestión de Usuarios como Superadmin

**Descripción:** Superadmin puede gestionar todos los usuarios, sus permisos, roles y estados.

| Función | Descripción | Status |
|---------|-----------|--------|
| Listar usuarios | Vista de todos los usuarios del sistema | Pendiente |
| Cambiar permisos | Asignar roles (admin, cuidador, paciente, etc.) | Pendiente |
| Suspender cuenta | Desactivar usuario sin eliminar datos | Pendiente |
| Auditoría | Log de qué hizo cada usuario y cuándo | Pendiente |

**Tests esperados:** 4

---

## 5.4 Funcionalidades de Monitoreo, Métricas y Analytics

### 5.4.1 Métricas y Analytics del Producto

**Historia:** HU-43 — Métricas y Analytics del Producto

**Descripción:** Dashboard de métricas sobre el uso de la aplicación y adopción de usuarios.

| Métrica | Descripción | Status |
|---------|-----------|--------|
| Usuarios activos | DAU (Daily Active Users), MAU (Monthly Active Users) | Pendiente |
| Pacientes registrados | Total y tendencia | Pendiente |
| Llamadas realizadas | Total por día/semana/mes | Pendiente |
| Tasa de confirmación | % de llamadas con respuesta positiva | Pendiente |
| Utilización de planes | Qué planes son más populares | Pendiente |
| Churn rate | % de usuarios que se van por mes | Pendiente |

**Herramientas:** Mixpanel, Amplitude, o Google Analytics con eventos custom.

**Tests esperados:** 3–4

---

### 5.4.2 Vigilancia del Sistema

**Historia:** HU-55 — Vigilancia del Sistema

**Descripción:** Monitoreo en tiempo real de salud del sistema: uptime, errores, latencia, recursos.

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Dashboard de uptime | Mostrar disponibilidad del sistema 24/7 | Pendiente |
| Alertas automáticas | Notificar si hay errores o caídas | Pendiente |
| Logs centralizados | Consolidar logs en Datadog o CloudWatch | Pendiente |
| Métricas de performance | CPU, memoria, tiempo de respuesta | Pendiente |

**Herramientas:** Datadog, New Relic, o Prometheus.

---

### 5.4.3 Métricas de Empresa

**Historia:** HU-56 — Métricas de Empresa

**Descripción:** Dashboard financiero y operacional para ejecutivos.

| Métrica | Descripción | Status |
|---------|-----------|--------|
| MRR (Ingresos recurrentes) | Ingresos mensuales predecibles | Pendiente |
| ARPU (Ingresos por usuario) | Promedio de ingresos por usuario activo | Pendiente |
| LTV (Lifetime Value) | Valor total esperado de un cliente | Pendiente |
| CAC (Customer Acquisition Cost) | Costo de adquirir un cliente | Pendiente |
| ROI de marketing | Retorno de inversión en campañas | Pendiente |
| Proyecciones | Forecast de crecimiento y rentabilidad | Pendiente |

**Herramientas:** Tableau, Power BI, o Google Data Studio.

---

## 5.5 Funcionalidades de Integraciones

### 5.5.1 Integración WhatsApp en Login

**Historia:** HU-57 — Integración WhatsApp en Login

**Descripción:** Permitir que los usuarios inicien sesión con su número de WhatsApp (autenticación alternativa).

| Componente | Descripción | Status |
|-----------|-----------|--------|
| Login con WhatsApp | Usar número de WhatsApp como identificador | Pendiente |
| Verificación OTP | Enviar código de un solo uso a WhatsApp | Pendiente |
| Vinculación de cuenta | Conectar cuenta existente con WhatsApp | Pendiente |
| Recuperación de contraseña | Reset enviado a WhatsApp | Pendiente |

**Servicios requeridos:**
- Twilio WhatsApp API
- Meta/WhatsApp Business API

**Tests esperados:** 4–5

---

## 5.6 Ejecución de Pruebas del Sistema

### 5.6.1 Ejecutar Pruebas del Sistema y Reporte de Errores

**Historia:** HU-44 — Ejecutar pruebas del sistema y reporte de errores

**Descripción:** Suite completa de pruebas funcionales, de integración y de extremo a extremo (E2E).

| Tipo de Prueba | Descripción | Status |
|---|---|---|
| Pruebas funcionales | Verificar cada funcionalidad principal | Pendiente |
| Pruebas de integración | Probar flujos entre módulos (auth → llamadas → notificaciones) | Pendiente |
| Pruebas E2E | Simular sesión completa de usuario real (Selenium, Cypress) | Pendiente |
| Pruebas de carga | Simular múltiples usuarios simultáneos | Pendiente |
| Pruebas de recuperación | Verificar recuperación ante fallos | Pendiente |

**Entregable:** Reporte de errores encontrados, severidad, pasos para reproducir, y estado de fixes.

**Tests esperados:** 15–20

---

## 5.7 Tests para Sprint 3

| Historia | Tests Planeados | Archivos |
|----------|---|---|
| HU-35 Dashboard multi-pacientes | 4 | `apps/dashboard/tests/test_multi_pacientes.py` |
| HU-36 Reportes exportables | 3 | `apps/reportes/tests/test_export.py` |
| HU-37 Notificaciones WhatsApp | 2 | `apps/notificaciones/tests/test_whatsapp.py` |
| HU-39 Validación de usuarios | 5 | `apps/autenticacion/tests/test_validacion.py` |
| HU-43 Analytics y Métricas | 4 | `apps/analytics/tests/test_metricas.py` |
| HU-44 Pruebas del sistema | 18 | `apps/sistema/tests/test_suite_completa.py` |
| HU-47 Seguridad e integridad | 8 | `apps/seguridad/tests/test_owasp.py` |
| HU-50 Panel Admin - Pagos | 5 | `apps/admin/tests/test_pagos.py` |
| HU-51 Historial transacciones | 3 | `apps/pagos/tests/test_historial.py` |
| HU-52 Códigos de acceso | 4 | `apps/pagos/tests/test_codigos.py` |
| HU-53 Sistema de tickets | 5 | `apps/soporte/tests/test_tickets.py` |
| HU-54 Gestión de usuarios admin | 4 | `apps/admin/tests/test_usuarios.py` |
| HU-55 Vigilancia del sistema | — | Herramientas externas (Datadog/New Relic) |
| HU-56 Métricas empresa | — | Dashboard BI (Tableau/Power BI) |
| HU-57 Login WhatsApp | 5 | `apps/autenticacion/tests/test_whatsapp_login.py` |
| **Total Sprint 3** | **~71 tests nuevos** | — |
| **Suite total (Sprint 2 + 3)** | **~173 tests** | — |

---

## 5.8 Status de Implementación

| Funcionalidad | Diseño | Implementación | Testing | Status |
|--------------|--------|---|---|---|
| HU-35 Dashboard Multi | Pendiente | Pendiente | Pendiente | Not Started |
| HU-36 Reportes | Pendiente | Pendiente | Pendiente | Not Started |
| HU-37 WhatsApp Notificaciones | Pendiente | Pendiente | Pendiente | Not Started |
| HO-40 Modelo Negocio y Monetización | En Progreso | — | — | In Progress (Doc) |
| HU-39 Validación usuarios | Pendiente | Pendiente | Pendiente | Not Started |
| HU-43 Analytics y Métricas | Pendiente | Pendiente | Pendiente | Not Started |
| HU-44 Pruebas sistema | Pendiente | Pendiente | Pendiente | Not Started |
| HU-47 Seguridad e integridad | Pendiente | Pendiente | Pendiente | Not Started |
| HU-50 Panel Admin - Pagos | Pendiente | Pendiente | Pendiente | Not Started |
| HU-51 Historial transacciones | Pendiente | Pendiente | Pendiente | Not Started |
| HU-52 Códigos de acceso | Pendiente | Pendiente | Pendiente | Not Started |
| HU-53 Tickets de soporte | Pendiente | Pendiente | Pendiente | Not Started |
| HU-54 Gestión usuarios admin | Pendiente | Pendiente | Pendiente | Not Started |
| HU-33 Compliance legal | Pendiente | — | — | In Progress (Legal Review) |
| HU-55 Vigilancia sistema | Pendiente | Pendiente | — | Not Started |
| HU-56 Métricas empresa | Pendiente | Pendiente | — | Not Started |
| HU-57 Login WhatsApp | Pendiente | Pendiente | Pendiente | Not Started |

---

---

# 6. Calidad del Software

Línea base de Sprint 2: **102 tests, 0 vulnerabilidades, PEP 8 compliance 100%**

## 6.1 Estándares de Código (Sin cambios respecto a Sprint 2)

El código sigue **PEP 8**:

- **Variables/funciones:** `nombre_usuario`, `crear_llamada()`
- **Clases:** `ReporteService`, `NotificacionWhatsApp`
- **Constantes:** `MAX_REINTENTOS`, `PLAN_PROFESIONAL`
- **Archivos:** `reporte_service.py`, `models.py`

---

## 6.2 Herramientas de Control de Calidad

| Herramienta | Métrica | Umbral | Status |
|-----------|---------|--------|--------|
| **ruff** | Estilo PEP 8 | 0 errores | Sprint 3 |
| **bandit** | Seguridad | 0 críticos/medios | Sprint 3 |
| **coverage** | Cobertura de tests | ≥ 80% | Sprint 3 |
| **Safety** | Dependencias vulnerables | 0 | Sprint 3 |

---

## 6.3 CI/CD (Igual a Sprint 2)

```yaml
# .github/workflows/tests.yml
on: [push, pull_request]
jobs:
  test:
    - ruff check
    - python manage.py test
    - coverage report --fail-under=80
```

**Comportamiento:** Merge bloqueado si algún test falla.

---

---

# 7. Lo que Haremos en Sprint 3

Sprint 3 es el sprint final. El objetivo es entregar una aplicación lista para producción validada con usuarios reales.

| Entregable | Descripción | Peso | Status |
|-----------|-----------|------|--------|
| **Caso de Negocio (v3)** | Finalizar análisis de viabilidad | 10% | En curso |
| **Pruebas de Usabilidad** | 8 sesiones con cuidadores reales + análisis de resultados | 20% | Planeado |
| **Manual de Usuario** | Guía completa con capturas o videos | 20% | Planeado |
| **Despliegue en Producción** | Aplicación accesible en URL pública + documentación | 10% | Planeado |
| **MVP Mejorado** | HU-35, HU-36, HU-37 + investigación HU-38 | 20% | Planeado |
| **Presentación Final** | Deck + demo + retrospectiva | 20% | Planeado |

---

---

# 8. Presentación Final (Sprint 3)

## 8.1 Estructura de la Presentación

**Duración:** 15–20 minutos (presentación) + 5 min (preguntas)

| Sección | Tiempo | Contenido |
|---------|--------|----------|
| **1. Contexto del Proyecto** | 2 min | Problema, solución, objetivo del sprint |
| **2. MVP Demostrado** | 5 min | Demo en vivo: registrar paciente → programar llamada → ver historial |
| **3. Resultados de Pruebas** | 3 min | Tasa de éxito usabilidad, puntos de fricción, ajustes aplicados |
| **4. Métricas de Ingeniería** | 2 min | Tests (111 total), cobertura, vulnerabilidades, CI/CD |
| **5. Despliegue y Acceso** | 2 min | URL de producción, cómo acceder, requisitos técnicos |
| **6. Caso de Negocio Final** | 2 min | Viabilidad técnica/operativa, punto de equilibrio, recomendación |
| **7. Aprendizajes y Próximos Pasos** | 2 min | Qué salió bien, qué mejorar, Sprint 4 (si aplica) |

---

## 8.2 Demo Planeada

**Escenario:** Registrar un nuevo paciente y ver cómo funciona una llamada automática.

**Pasos:**
1. Abrir `porvoz.com` (producción)
2. Ingreso: usuario "demo" / contraseña "demo"
3. Crear nuevo paciente: "Maria Garcia", 1958-05-15, teléfono XXX
4. Agregar medicamento: "Losartán 50mg", 08:00, "Tomar en ayunas"
5. Mostrar historial (con datos de prueba preexistentes)
6. Mostrar dashboard con estadísticas

**Duración:** 3–4 minutos máximo.

---

## 8.3 Materiales de Presentación

| Material | Contenido | Status |
|----------|-----------|--------|
| **Deck** (PowerPoint/Canva) | Slides con branding, gráficos, resultados | ⏳ |
| **Video de demostración** | Respaldo en caso de falla de conexión | ⏳ |
| **Documento ejecutivo** | 1 página con resumen y recomendaciones | ⏳ |
| **Preguntas preparadas** | Respuestas a objeciones probables | ⏳ |

---

## 8.4 Logística

| Item | Responsable | Status |
|------|-------------|--------|
| Reservar sala | — | ⏳ |
| Proyector / pantalla | — | ⏳ |
| Audio | — | ⏳ |
| Acceso a WiFi | — | ⏳ |
| Conexión a internet para demo en vivo | — | ⏳ |

---

---

# 9. Evidencias de Ceremonias – Sprint 3

## 9.1 Sprint Planning

| Fecha | Asistentes | Decisiones |
|-------|-----------|-----------|
| [Insertar] | — | — |

---

## 9.2 Daily Standups

| Fecha | Update | Bloqueadores |
|-------|--------|---|
| [Insertar] | — | — |
| [Insertar] | — | — |

---

## 9.3 Sprint Review

| Fecha | Histórico | Feedback |
|-------|---|---|
| [Insertar] | — | — |

---

## 9.4 Retrospectiva

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué salió bien? | — |
| ¿Qué no salió bien? | — |
| ¿Qué mejorar? | — |

---

## 9.5 Evidencias Visuales

**Fotos de reuniones, capturas de pantalla de trabajos en progreso, etc.**

[Insertar imágenes aquí]

---

---

# Notas Finales

**Sprint 3 es el cierre del MVP entregable.** Una vez completados los entregables arriba, Porvoz estará listo para:

1. ✅ Demo a stakeholders
2. ✅ Pruebas con usuarios reales
3. ✅ Acceso público en URL
4. ✅ Manual completo para clientes
5. ✅ Caso de negocio validado

**Próximas fases (post-Sprint 3):**
- Sprint 4 (si aplica): Mejoras complejas de usabilidad, panel de médicos, SMS alerts
- Lanzamiento formal con primeros clientes piloto
- Escala a producción completa
- Implementación de sistema de pagos y planes premium

---

**Responsables:** Matías Martínez + equipo  
**Última actualización:** 12 de mayo de 2026  
**Estado:** Planning Phase
