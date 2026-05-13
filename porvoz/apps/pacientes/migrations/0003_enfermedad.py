from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pacientes", "0002_paciente_foto_descripcion"),
    ]

    operations = [
        migrations.CreateModel(
            name="Enfermedad",
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
                    models.CharField(
                        max_length=200, verbose_name="Nombre de la enfermedad"
                    ),
                ),
                (
                    "descripcion",
                    models.TextField(blank=True, verbose_name="Descripción"),
                ),
                (
                    "diagnostico_fecha",
                    models.DateField(
                        blank=True, null=True, verbose_name="Fecha de diagnóstico"
                    ),
                ),
                ("activa", models.BooleanField(default=True, verbose_name="Activa")),
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
                    "paciente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enfermedades",
                        to="pacientes.paciente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Enfermedad",
                "verbose_name_plural": "Enfermedades",
                "db_table": "porvoz_enfermedad",
            },
        ),
        migrations.AddIndex(
            model_name="enfermedad",
            index=models.Index(
                fields=["paciente", "activa"], name="porvoz_enfe_paciente_idx"
            ),
        ),
    ]
