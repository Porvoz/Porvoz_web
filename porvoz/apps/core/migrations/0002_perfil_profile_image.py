from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("porvoz", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="profile_image",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_images/", verbose_name="Foto de perfil"
            ),
        ),
    ]
