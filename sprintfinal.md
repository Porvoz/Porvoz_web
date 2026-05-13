# Caso de Negocio – Tercera Versión (Final)

**Proyecto:** Porvoz — Sistema de Recordatorios de Medicamentos con Llamadas de Voz  
**Versión:** 3.0 (Final)  
**Fecha:** Mayo 2026  
**Estado:** MVP Completado y Desplegado

---

# 1. Resumen Ejecutivo

Porvoz resuelve el problema de adherencia medicamentosa en pacientes crónicos (50% incumplimiento según OMS) mediante un sistema automatizado de recordatorios por voz con clasificación inteligente de respuestas.

Evidencia de entrega: 112 tests pasando, 0 vulnerabilidades, despliegue operacional en AWS, compliance legal incluido, panel de administración y pagos implementado.

Estado: Listo para clientes piloto.

---

# 2. Viabilidad del Proyecto

## 2.1 Análisis de Viabilidad

### Viabilidad Técnica

El proyecto es técnicamente viable. Se implementó el stack completo: Django + PostgreSQL + Redis + Celery + Twilio + Google Gemini. La suite de 112 tests pasa con 0 vulnerabilidades críticas. El CI/CD con GitHub Actions garantiza integración continua. Los webhooks de Twilio funcionan con validación de seguridad y el sistema de tareas asincrónicas maneja reintentos automáticos sin intervención humana.

---

### Viabilidad Operativa

**Equipo mínimo requerido:**
- 1 Backend Engineer (Django + Celery)
- 1 DevOps Engineer (AWS + Docker + PostgreSQL)
- 1 Frontend/UX Designer
- 2-4 horas semanales de monitoreo

**Monitoreo y SLA:**
Infraestructura en AWS EC2 (t3.medium) + RDS PostgreSQL + ElastiCache Redis. Disponibilidad esperada del 99.5% con tiempo de respuesta menor a 2 segundos. Email automático ante errores críticos. Backups diarios en PostgreSQL. Celery puede distribuirse en múltiples workers si el volumen crece.

---

### Viabilidad de Mercado

**Validación con usuarios:**
COMPLETA ESTE CAMPO

**Disposición a pagar:**
COMPLETA ESTE CAMPO

---

### Costo-Beneficio

| Aspecto | Año 1 | Observación |
|---------|-------|-------------|
| Ingresos estimados | COMPLETA ESTE CAMPO | Depende de modelo de pricing |
| Costos operativos | ~$15K-20K USD | AWS ($450/mes) + Twilio ($0.025-0.10/llamada) + personal |
| Break-even | COMPLETA ESTE CAMPO | Depende de volumen de usuarios |

---

## 2.2 Conclusión de Viabilidad

El proyecto es viable en todas las dimensiones. Técnicamente el stack es robusto con APIs integradas y tests completos. Operativamente la infraestructura es escalable con un equipo pequeño. El problema tiene demanda real (50% incumplimiento OMS) y los costos son controlados.

**Recomendación final:** Proceder con fase piloto. El MVP está en producción y listo para validar el fit mercado-producto con clientes reales.

---

# 3. Pruebas de Usabilidad

## 3.1 Protocolo Ejecutado

**¿Se aplicaron todas las tareas definidas?**
COMPLETA ESTE CAMPO (Sí/No)

**Tareas ejecutadas:**
COMPLETA ESTE CAMPO

---

**¿Se reclutaron participantes representativos?**
COMPLETA ESTE CAMPO (Sí/No)

**Perfil de participantes:**
- Número total: COMPLETA ESTE CAMPO
- Edad promedio: COMPLETA ESTE CAMPO
- Experiencia técnica: COMPLETA ESTE CAMPO
- Representatividad al público objetivo: COMPLETA ESTE CAMPO

---

**¿Se formularon correctamente las preguntas de seguimiento?**
COMPLETA ESTE CAMPO (Sí/No)

**Observaciones:**
COMPLETA ESTE CAMPO

---

## 3.2 Resultados Recopilados

### Datos Cuantitativos

| Métrica | Resultado | Meta |
|---------|-----------|------|
| Tasa de éxito (tareas completadas) | COMPLETA ESTE CAMPO | >= 75% |
| Tiempo promedio por tarea | COMPLETA ESTE CAMPO | — |
| Puntuación SUS (System Usability Scale) | COMPLETA ESTE CAMPO | >= 68% |
| Tasa de recomendación | COMPLETA ESTE CAMPO | >= 75% |

---

### Datos Cualitativos

**Principales hallazgos:**
1. COMPLETA ESTE CAMPO
2. COMPLETA ESTE CAMPO
3. COMPLETA ESTE CAMPO

**Puntos de fricción identificados:**
COMPLETA ESTE CAMPO

**Fortalezas observadas:**
COMPLETA ESTE CAMPO

---

## 3.3 Análisis de Resultados

**¿Se hizo un análisis correcto y conclusiones congruentes?**
COMPLETA ESTE CAMPO (Sí/No)

**Conclusiones por hipótesis:**

| Hipótesis | Validada | Observaciones |
|-----------|----------|---|
| COMPLETA ESTE CAMPO | Sí / No | — |
| COMPLETA ESTE CAMPO | Sí / No | — |
| COMPLETA ESTE CAMPO | Sí / No | — |

---

## 3.4 Ajustes Implementados

**Cambios aplicados antes de entrega:**

| Ajuste | Complejidad | Estado |
|--------|-------------|--------|
| COMPLETA ESTE CAMPO | Baja/Media | Hecho |
| COMPLETA ESTE CAMPO | Baja/Media | Hecho |

---

**Cambios propuestos para futuro:**

| Mejora | Justificación | Estimación |
|--------|---|---|
| COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO | — |
| COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO | — |

---

# 4. Manual de Usuario

## 4.1 Disponibilidad del Manual

**Formato del manual:**
COMPLETA ESTE CAMPO (PDF / Video tutorial / Integrado en la aplicación / Otro)

**Link o ubicación:**
COMPLETA ESTE CAMPO

---

## 4.2 Evaluación del Manual

**¿Explica paso a paso cómo usar las funciones principales?**
COMPLETA ESTE CAMPO (Sí completamente / Parcialmente / No)

**Ejemplo de instrucción (incluir fragmento):**
COMPLETA ESTE CAMPO

---

**¿Incluye capturas de pantalla, videos o diagramas?**
COMPLETA ESTE CAMPO (Sí/No)

**Cantidad de elementos visuales:**
- Capturas: COMPLETA ESTE CAMPO
- Diagramas: COMPLETA ESTE CAMPO
- Videos: COMPLETA ESTE CAMPO

**¿Facilitan la comprensión?**
COMPLETA ESTE CAMPO

---

## 4.3 Cobertura de Funcionalidades

| Funcionalidad | Documentada | Ejemplos |
|---|---|---|
| Registro de pacientes | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO |
| Agregar medicamentos | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO |
| Ver historial | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO |
| Configurar notificaciones | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO |
| Cambiar contraseña | COMPLETA ESTE CAMPO | COMPLETA ESTE CAMPO |

---

# 5. Despliegue de la Aplicación

## 5.1 Aplicación Desplegada

La aplicación está desplegada en AWS EC2 (t3.medium) con PostgreSQL RDS 16 y ElastiCache Redis 7. Es accesible desde internet en http://34.198.74.65.

**Credenciales de prueba:**
- Usuario: COMPLETA ESTE CAMPO
- Contraseña: COMPLETA ESTE CAMPO

---

## 5.2 Estado Funcional

Todas las funcionalidades están operacionales: registro de pacientes, configuración de medicamentos, llamadas automáticas, clasificación de respuestas con IA, reintentos automáticos, historial de llamadas, notificaciones por email, dashboard de estadísticas y panel de administración.

---

## 5.3 Tipo de Despliegue

El despliegue es mantenible y escalable. La aplicación está dockerizada en 6 servicios (web, celery-worker, celery-beat, PostgreSQL, Redis, nginx). El CI/CD con GitHub Actions corre los tests en cada push/PR. La configuración está centralizada en variables de entorno. Los workers de Celery se pueden multiplicar horizontalmente y RDS soporta failover automático.

---

## 5.4 Documentación de Despliegue

La documentación está completa en README.md, .env.example, docker-compose.yml y DEPLOYMENT.md. Los pasos son: clonar el repositorio, configurar .env con las credenciales correspondientes, ejecutar `docker-compose up -d`, correr migraciones con `docker-compose exec web python manage.py migrate` y acceder por HTTP al IP público.

---

# 6. Desarrollo de Código

## 6.1 MVP Funcional

Todas las funcionalidades planeadas están implementadas y operacionales:

| Funcionalidad | Estado |
|---|---|
| Llamadas automáticas | Operacional con Twilio + Gemini |
| Historial de llamadas | Filtrable por resultado y fecha |
| Notificaciones por email | Con preferencias de usuario |
| Dashboard | Estadísticas en tiempo real |
| Panel de administración | Gestión de usuarios y pacientes |
| Confirmación de toma | Clasificación por IA de respuestas |
| Reintentos automáticos | Configurable por medicamento |
| Recuperación de contraseña | Flujo seguro por email |

---

## 6.2 Historias de Usuario Implementadas

Total planeadas: 11 HUs — Total completadas: 11 HUs — Porcentaje: 100%

| HU | Descripción | Estado |
|-----|---|---|
| HU-04 | Llamadas automáticas con IA | Completada |
| HU-05 | Registrar confirmación de toma | Completada |
| HU-07 | Validación y manejo de errores | Completada |
| HU-09 | Detectar respuestas negativas | Completada |
| HU-11 | Dashboard básico | Completada |
| HU-27 | Recuperar contraseña | Completada |
| HU-29 | Historial de llamadas | Completada |
| HU-30 | Notificaciones de emergencia | Completada |
| HU-31 | Sistema de acciones post-llamada | Completada |
| HU-32 | Integración notificaciones + correo | Completada |
| HU-34 | Responsive en celular | Completada |

---

## 6.3 Gestión Técnica

Git se usó adecuadamente con commits claros y organizados, ramas por feature y pull requests documentadas. El repositorio acumula 132 commits en total, más de 8 pull requests mergeadas a main y 7 ramas creadas. El código completo del MVP está en https://github.com/Porvoz/Porvoz_web.

---

## 6.4 Calidad del Código

| Métrica | Resultado | Meta |
|---------|-----------|------|
| Tests pasando | 142 | 80+ |
| Cobertura | COMPLETA ESTE CAMPO % | >= 80% |
| Vulnerabilidades críticas | 0 | 0 |
| Errores en CI/CD | 0 | 0 |
| Tiempo de ejecución suite | ~75 segundos | < 120s |

Se agregaron 30 tests al panel de administración que cubren el ciclo completo de códigos de acceso (generación, unicidad, canje exitoso, código inexistente, ya usado y expirado por fecha límite), el cálculo automático de costos y ganancia neta en pagos históricos, los métodos de margen en ConfiguracionPlan, las propiedades de tickets de soporte para usuarios registrados y visitantes anónimos, y el control de acceso a todas las vistas del panel confirmando que usuarios sin sesión o sin permisos de staff sean redirigidos.

---

## 6.5 Funcionalidades Adicionales del Sprint Final

Más allá del core del sistema de llamadas, el equipo implementó un conjunto de historias que completan el producto como plataforma comercial. Julián Lara se encargó de HU-45 (Despliegue y operación), dejando la aplicación corriendo en producción sobre AWS con Docker y configuración de entorno completa. Luis Ramírez y Matías Martínez desarrollaron HU-47 (Pruebas y medidas de seguridad e integridad de la webapp), que incluye validación de firmas de webhooks, protección CSRF, sanitización de entradas y suite de tests de seguridad. Samuel Cardoza implementó HU-40 (Modelo de Negocio y Estrategia de Monetización), definiendo los planes de suscripción y la lógica de acceso por plan. Nathalia Cardoza construyó HU-50 (Panel de Administración - Gestión de Pagos) con la vista administrativa para gestionar transacciones y suscripciones activas. HU-43 y HU-51 (Métricas y Analytics del Producto e Historial de Transacciones) fueron desarrolladas en conjunto, dando al administrador visibilidad completa sobre el uso de la plataforma y el historial financiero. Luis Ramírez también se encargó de HU-44 (Ejecutar pruebas del sistema y reporte de errores), consolidando la suite de pruebas y generando el reporte de errores identificados. HU-33 (Compliance y Aspectos Legales en Salud) integró los requisitos HIPAA/GDPR en la plataforma, incluyendo políticas de privacidad y términos de uso. Finalmente, Matías Martínez implementó HU-56 (Métricas de Empresa) y HU-52 (Códigos de Acceso a Planes), que permiten al administrador monitorear el crecimiento del negocio y gestionar códigos promocionales para acceso a planes de suscripción.

---

# 7. Conclusiones Finales

## Cumplimiento de Requisitos

**Caso de Negocio:** Viable técnicamente, viable operativamente, recomendado para lanzamiento.

**Pruebas de Usabilidad:** COMPLETA ESTE CAMPO (requiere ejecución con usuarios reales)

**Manual de Usuario:** COMPLETA ESTE CAMPO (requiere documentación formal)

**Despliegue:** Aplicación accesible en http://34.198.74.65, documentación de despliegue lista. Monitoreo: COMPLETA ESTE CAMPO.

**Código:** MVP con todas las funcionalidades implementadas, 142 tests pasando, repositorio organizado con 132 commits.

---

## Estado Final

El proyecto está listo para clientes piloto. El sistema está desplegado en AWS, todas las funcionalidades clave implementadas, 142 tests pasando, integración con APIs externas validada y documentación técnica completa.

**Recomendaciones para mejora:**

| Mejora | Justificación | Prioridad |
|--------|---|---|
| SMS como alternativa a email | Aumentar alcance de notificaciones | Media |
| Login social (Google/Facebook) | Reducir fricción en registro | Baja |
| Reportes exportables (PDF/Excel) | Facilitar análisis de adherencia | Media |
| Alertas en tiempo real con WebSockets | Mejor experiencia de monitoreo | Baja |

---

**Responsables:** Matías Martínez + Equipo  
**Última actualización:** 13 de mayo de 2026  
**Estado:** Completado — Listo para Presentación
