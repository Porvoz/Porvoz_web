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
            name="Perfil",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("caregiver", "Cuidador"), ("patient", "Paciente")], max_length=20, verbose_name="Rol")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="Nombre")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="Apellidos")),
                ("date_of_birth", models.DateField(blank=True, null=True, verbose_name="Fecha de nacimiento")),
                ("city", models.CharField(blank=True, max_length=100, verbose_name="Ciudad")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="Teléfono")),
                (
                    "document_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("cc", "Cédula de ciudadanía"),
                            ("ce", "Cédula de extranjería"),
                            ("ti", "Tarjeta de identidad"),
                            ("pp", "Pasaporte"),
                        ],
                        max_length=10,
                        verbose_name="Tipo de documento",
                    ),
                ),
                ("document_number", models.CharField(blank=True, max_length=30, verbose_name="Número de documento")),
                ("emergency_contact_name", models.CharField(blank=True, max_length=150, verbose_name="Nombre contacto de emergencia")),
                ("emergency_contact_phone", models.CharField(blank=True, max_length=30, verbose_name="Teléfono contacto de emergencia")),
                ("profile_completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil",
                "verbose_name_plural": "Perfiles",
                "db_table": "porvoz_perfil",
            },
        ),
    ]

