from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Paciente",
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
                    "nombre",
                    models.CharField(max_length=200, verbose_name="Nombre completo"),
                ),
                ("telefono", models.CharField(max_length=30, verbose_name="Teléfono")),
                (
                    "es_usuario_mismo",
                    models.BooleanField(
                        default=False,
                        help_text="True si este paciente es el mismo usuario que lo creó",
                        verbose_name="Es el usuario mismo",
                    ),
                ),
                (
                    "fecha_nacimiento",
                    models.DateField(
                        blank=True, null=True, verbose_name="Fecha de nacimiento"
                    ),
                ),
                (
                    "notas",
                    models.TextField(blank=True, verbose_name="Notas adicionales"),
                ),
                ("activo", models.BooleanField(default=True, verbose_name="Activo")),
                (
                    "creado_en",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "actualizado_en",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de actualización"
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pacientes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Paciente",
                "verbose_name_plural": "Pacientes",
                "db_table": "porvoz_paciente",
            },
        ),
        migrations.AddIndex(
            model_name="paciente",
            index=models.Index(
                fields=["usuario", "activo"], name="porvoz_paci_usuario_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="paciente",
            unique_together={("usuario", "telefono")},
        ),
    ]
