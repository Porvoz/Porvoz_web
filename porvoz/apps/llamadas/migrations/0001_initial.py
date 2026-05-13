from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pacientes", "0001_initial"),
        ("medicamentos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notificacion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("llamada", "Llamada"),
                            ("recordatorio", "Recordatorio"),
                            ("alerta", "Alerta"),
                            ("sistema", "Sistema"),
                        ],
                        default="llamada",
                        max_length=20,
                        verbose_name="Tipo de notificación",
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("enviada", "Enviada"),
                            ("atendida", "Atendida"),
                            ("no_atendida", "No atendida"),
                            ("fallida", "Fallida"),
                        ],
                        default="pendiente",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                ("titulo", models.CharField(max_length=200, verbose_name="Título")),
                ("mensaje", models.TextField(blank=True, verbose_name="Mensaje")),
                (
                    "fecha_programada",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fecha programada"
                    ),
                ),
                (
                    "fecha_enviada",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fecha enviada"
                    ),
                ),
                (
                    "fecha_atendida",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Fecha atendida"
                    ),
                ),
                ("leida", models.BooleanField(default=False, verbose_name="Leída")),
                (
                    "creado_en",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "medicamento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notificaciones",
                        to="medicamentos.medicamento",
                        verbose_name="Medicamento",
                    ),
                ),
                (
                    "paciente",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones",
                        to="pacientes.paciente",
                        verbose_name="Paciente",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificación",
                "verbose_name_plural": "Notificaciones",
                "db_table": "porvoz_notificacion",
                "ordering": ["-creado_en"],
            },
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(
                fields=["usuario", "leida"], name="porvoz_noti_usuario_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(
                fields=["usuario", "tipo"], name="porvoz_noti_usuario_tipo_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(fields=["paciente"], name="porvoz_noti_paciente_idx"),
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(
                fields=["fecha_programada"], name="porvoz_noti_fecha_pr_idx"
            ),
        ),
    ]
