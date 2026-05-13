from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("porvoz", "0002_perfil_profile_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="perfil",
            name="role",
        ),
    ]
