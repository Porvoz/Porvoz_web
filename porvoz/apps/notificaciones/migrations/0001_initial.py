"""
Migración inicial de la app notificaciones.

Usa SeparateDatabaseAndState para "adoptar" la tabla existente
porvoz_notificacion creada por apps.llamadas, sin modificar la BD.
No se pierden datos.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Adopta el modelo Notificacion desde apps.llamadas sin tocar la BD.

    SeparateDatabaseAndState tiene dos sublistas:
    - state_operations: lo que Django registra en su estado interno (crear el modelo aquí).
    - database_operations: lo que se ejecuta en la BD (vacío → no hace nada en la BD).
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pacientes", "0001_initial"),
        ("medicamentos", "0001_initial"),
        # Depende de que llamadas ya haya creado la tabla en la BD.
        ("llamadas", "0002_rename_porvoz_noti_usuario_idx_porvoz_noti_usuario_4220f6_idx_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Estado: Django aprende que Notificacion existe en esta app.
            state_operations=[
                migrations.CreateModel(
                    name="Notificacion",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("tipo", models.CharField(choices=[("llamada", "Llamada"), ("recordatorio", "Recordatorio"), ("alerta", "Alerta"), ("sistema", "Sistema")], default="llamada", max_length=20, verbose_name="Tipo de notificación")),
                        ("estado", models.CharField(choices=[("pendiente", "Pendiente"), ("enviada", "Enviada"), ("atendida", "Atendida"), ("no_atendida", "No atendida"), ("fallida", "Fallida")], default="pendiente", max_length=20, verbose_name="Estado")),
                        ("titulo", models.CharField(max_length=200, verbose_name="Título")),
                        ("mensaje", models.TextField(blank=True, verbose_name="Mensaje")),
                        ("fecha_programada", models.DateTimeField(blank=True, null=True, verbose_name="Fecha programada")),
                        ("fecha_enviada", models.DateTimeField(blank=True, null=True, verbose_name="Fecha enviada")),
                        ("fecha_atendida", models.DateTimeField(blank=True, null=True, verbose_name="Fecha atendida")),
                        ("leida", models.BooleanField(default=False, verbose_name="Leída")),
                        ("creado_en", models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")),
                        ("medicamento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notificaciones", to="medicamentos.medicamento", verbose_name="Medicamento")),
                        ("paciente", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones", to="pacientes.paciente", verbose_name="Paciente")),
                        ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones", to=settings.AUTH_USER_MODEL, verbose_name="Usuario")),
                    ],
                    options={
                        "verbose_name": "Notificación",
                        "verbose_name_plural": "Notificaciones",
                        "db_table": "porvoz_notificacion",
                        "ordering": ["-creado_en"],
                    },
                ),
            ],
            # BD: no hacer nada, la tabla ya existe creada por llamadas.
            database_operations=[],
        ),
    ]
