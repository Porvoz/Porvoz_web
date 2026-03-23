"""
Migración para eliminar el modelo Notificacion del estado de la app llamadas.

Usa SeparateDatabaseAndState: Django deja de reconocer el modelo aquí,
pero la tabla porvoz_notificacion en la BD no se toca.
La tabla ahora es gestionada por apps.notificaciones.
"""
from django.db import migrations


class Migration(migrations.Migration):
    """Elimina Notificacion del estado de llamadas sin tocar la BD."""

    dependencies = [
        ("llamadas", "0002_rename_porvoz_noti_usuario_idx_porvoz_noti_usuario_4220f6_idx_and_more"),
        # Debe correr después de que notificaciones adopte la tabla.
        ("notificaciones", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Estado: Django olvida que Notificacion existía aquí.
            state_operations=[
                migrations.DeleteModel(name="Notificacion"),
            ],
            # BD: no hacer nada, la tabla la sigue usando notificaciones.
            database_operations=[],
        ),
    ]
