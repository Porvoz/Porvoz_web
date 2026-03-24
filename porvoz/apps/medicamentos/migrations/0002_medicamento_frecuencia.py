from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("medicamentos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicamento",
            name="frecuencia_tipo",
            field=models.CharField(
                choices=[("horario", "Horario específico"), ("cada_x_horas", "Cada X horas")],
                default="horario",
                max_length=20,
                verbose_name="Tipo de frecuencia",
            ),
        ),
        migrations.AddField(
            model_name="medicamento",
            name="cada_x_horas",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Para frecuencia 'Cada X horas' (ej: 8 = cada 8 horas)",
                null=True,
                verbose_name="Cada cuántas horas",
            ),
        ),
        migrations.AddField(
            model_name="medicamento",
            name="hora_inicio",
            field=models.TimeField(
                blank=True,
                help_text="Hora de inicio para 'Cada X horas' (ej: 08:00)",
                null=True,
                verbose_name="Hora de inicio",
            ),
        ),
        migrations.AlterField(
            model_name="medicamento",
            name="horario",
            field=models.TimeField(
                blank=True,
                help_text="Para frecuencia 'Horario específico'",
                null=True,
                verbose_name="Horario de toma",
            ),
        ),
    ]

