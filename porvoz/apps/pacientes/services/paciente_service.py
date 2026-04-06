"""
Servicio para gestión de pacientes.
"""

import unicodedata
from datetime import date, datetime
from typing import Optional, Tuple

from django.contrib.auth.models import User

from apps.pacientes.models import Paciente, Enfermedad


class PacienteService:

    @staticmethod
    def normalizar_busqueda(texto: str) -> str:
        """Minúsculas y sin tildes para búsqueda insensible."""
        if not texto:
            return ""
        texto = texto.lower().strip()
        nfd = unicodedata.normalize("NFD", texto)
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    @staticmethod
    def buscar_pacientes(pacientes: list, buscar: str) -> list:
        """Filtra pacientes por nombre (búsqueda normalizada)."""
        if not buscar:
            return pacientes
        buscar_norm = PacienteService.normalizar_busqueda(buscar)
        return [
            p
            for p in pacientes
            if buscar_norm
            in PacienteService.normalizar_busqueda(p.get_display_nombre())
        ]

    @staticmethod
    def verificar_telefono_existente(
        usuario: User, telefono: str, paciente_excluir_id: Optional[int] = None
    ) -> bool:
        """Verifica si ya existe un paciente con ese teléfono."""
        qs = Paciente.objects.filter(usuario=usuario, telefono=telefono, activo=True)
        if paciente_excluir_id:
            qs = qs.exclude(id=paciente_excluir_id)
        return qs.exists()

    @staticmethod
    def sanitize_phone(telefono: str) -> str:
        """Elimina espacios y guiones de un teléfono."""
        if not telefono:
            return ""
        return telefono.replace(" ", "").replace("-", "")

    @staticmethod
    def es_telefono_usuario_mismo(perfil_phone: str, telefono: str) -> bool:
        """Verifica si el teléfono pertenece al usuario (por coincidencia)."""
        if not perfil_phone or not telefono:
            return False
        telefono_norm = PacienteService.sanitize_phone(telefono)
        perfil_norm = PacienteService.sanitize_phone(perfil_phone)
        return perfil_norm.endswith(telefono_norm) or telefono_norm in perfil_norm

    @staticmethod
    def listar_pacientes(usuario: User, ordenar: str = "recientes") -> list:
        """Lista pacientes con ordenamiento."""
        return (
            Paciente.objects.filter(usuario=usuario, activo=True)
            .select_related("usuario", "usuario__perfil")
            .prefetch_related("medicamentos", "enfermedades")
        )

    @staticmethod
    def obtener_por_id(paciente_id: int, usuario: User) -> Optional[Paciente]:
        """Obtiene un paciente por ID verificando pertenencia."""
        try:
            return Paciente.objects.get(id=paciente_id, usuario=usuario)
        except Paciente.DoesNotExist:
            return None

    @staticmethod
    def crear_paciente(
        usuario: User,
        nombre: str,
        telefono: str,
        es_usuario_mismo: bool = False,
        **kwargs,
    ) -> Paciente:
        """Crea un nuevo paciente."""
        return Paciente.objects.create(
            usuario=usuario,
            nombre=nombre,
            telefono=telefono,
            es_usuario_mismo=es_usuario_mismo,
            **kwargs,
        )

    @staticmethod
    def crear_enfermedad(
        paciente: Paciente, nombre: str, descripcion: str = "", diagnostico_fecha=None
    ) -> Enfermedad:
        """Crea una enfermedad para un paciente."""
        return Enfermedad.objects.create(
            paciente=paciente,
            nombre=nombre,
            descripcion=descripcion,
            diagnostico_fecha=diagnostico_fecha,
        )

    @staticmethod
    def obtener_por_id_y_enfermedad(
        paciente_id: int, enfermedad_id: int, usuario: User
    ) -> tuple[Optional[Paciente], Optional[Enfermedad]]:
        """Obtiene paciente y enfermedad verificando pertenencia."""
        paciente = PacienteService.obtener_por_id(paciente_id, usuario)
        if not paciente:
            return None, None
        try:
            enfermedad = Enfermedad.objects.get(id=enfermedad_id, paciente=paciente)
            return paciente, enfermedad
        except Enfermedad.DoesNotExist:
            return paciente, None

    @staticmethod
    def parsear_fecha_diagnostico(
        fecha_str: str,
    ) -> Tuple[Optional[date], Optional[str]]:
        """Parsea y valida una fecha de diagnóstico.

        Returns:
            (date, None) si es válida, (None, mensaje_error) si no lo es.
        """
        if not fecha_str:
            return None, None
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha > date.today():
                return None, "La fecha de diagnóstico no puede ser futura."
            return fecha, None
        except ValueError:
            return None, None

    @staticmethod
    def reemplazar_enfermedades(paciente: Paciente, condiciones: list) -> None:
        """Elimina todas las enfermedades del paciente y crea las nuevas."""
        paciente.enfermedades.all().delete()
        for nombre_condicion in condiciones:
            Enfermedad.objects.create(
                paciente=paciente, nombre=nombre_condicion, descripcion=""
            )

    @staticmethod
    def copiar_foto_perfil_a_paciente(paciente: Paciente, perfil) -> None:
        """Copia la foto del perfil del usuario al paciente si no tiene foto propia."""
        if perfil and perfil.profile_image and not paciente.foto:
            try:
                from django.core.files.images import ImageFile
                from io import BytesIO

                if perfil.profile_image.storage.exists(perfil.profile_image.name):
                    imagen = perfil.profile_image.open("rb")
                    contenido = BytesIO(imagen.read())
                    contenido.seek(0)
                    img_name = perfil.profile_image.name.split("/")[-1]
                    nombre_archivo = f"paciente_{paciente.id}_{img_name}"
                    paciente.foto.save(nombre_archivo, ImageFile(contenido), save=True)
                    imagen.close()
            except (IOError, OSError):
                # Si falla la copia de imagen, continuamos sin ella
                pass
