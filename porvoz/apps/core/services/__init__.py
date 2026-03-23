# Services han sido movidos a sus apps respectivas:
# - RegistroService → apps.autenticacion.services
# - PerfilService → apps.usuarios.services
# - DashboardService → apps.dashboard.services
# - TelefonoService → apps.shared.services
# - obtener_planes → apps.shared.services
#
# Para mantener compatibilidad hacia atrás, se re-exportan desde aquí:
from apps.autenticacion.services import RegistroService
from apps.usuarios.services import PerfilService
from apps.dashboard.services import DashboardService
from apps.shared.services import TelefonoService, obtener_planes

__all__ = [
    "DashboardService",
    "TelefonoService",
    "obtener_planes",
    "RegistroService",
    "PerfilService",
]
