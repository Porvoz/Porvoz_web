# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("porvoz", "0003_remove_perfil_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="plan",
            field=models.CharField(
                choices=[
                    ("freemium", "Freemium"),
                    ("growth", "Growth Plan"),
                    ("multi_business", "Multi-business"),
                ],
                default="freemium",
                help_text="Plan de suscripción del usuario",
                max_length=20,
                verbose_name="Plan",
            ),
        ),
    ]
