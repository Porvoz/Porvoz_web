from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pacientes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paciente",
            name="foto",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="pacientes_fotos/",
                verbose_name="Foto del paciente",
            ),
        ),
        migrations.AddField(
            model_name="paciente",
            name="descripcion",
            field=models.TextField(
                blank=True,
                help_text="Información adicional sobre el paciente",
                verbose_name="Descripción",
            ),
        ),
    ]
