from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("pacientes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Medicamento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("nombre", models.CharField(max_length=200, verbose_name="Nombre del medicamento")),
                (
                    "dosis",
                    models.CharField(
                        help_text="Ej: 1 tableta, 500mg, etc.", max_length=100, verbose_name="Dosis"
                    ),
                ),
                ("horario", models.TimeField(verbose_name="Horario de toma")),
                ("activo", models.BooleanField(default=True, verbose_name="Activo")),
                (
                    "creado_en",
                    models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación"),
                ),
                (
                    "actualizado_en",
                    models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización"),
                ),
                (
                    "paciente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="medicamentos",
                        to="pacientes.paciente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Medicamento",
                "verbose_name_plural": "Medicamentos",
                "db_table": "porvoz_medicamento",
            },
        ),
        migrations.AddIndex(
            model_name="medicamento",
            index=models.Index(fields=["paciente", "activo"], name="porvoz_medi_paciente_idx"),
        ),
        migrations.AddIndex(
            model_name="medicamento",
            index=models.Index(fields=["horario"], name="porvoz_medi_horario_idx"),
        ),
    ]
