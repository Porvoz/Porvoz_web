from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_panel", "0005_configuracionplan"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuracionplan",
            name="plan",
            field=models.CharField(
                db_index=True,
                help_text="Clave interna del plan (slug único, ej: plan_empresa)",
                max_length=50,
                unique=True,
            ),
        ),
    ]
