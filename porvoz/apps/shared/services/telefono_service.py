"""
Servicio para parsing y formateo de números de teléfono.
"""

from dataclasses import dataclass


@dataclass
class TelefonoParseado:
    pais: str
    numero: str
    completo: str


class TelefonoService:

    PREFIJOS_COMUNES = {
        "+57": "Colombia",
        "+1": "USA/Canadá",
        "+34": "España",
        "+52": "México",
        "+54": "Argentina",
        "+55": "Brasil",
        "+56": "Chile",
        "+51": "Perú",
        "+593": "Ecuador",
        "+58": "Venezuela",
    }

    @classmethod
    def parsear_telefono(cls, telefono: str) -> TelefonoParseado:
        """
        Parsea un número de teléfono y retorna país y número separados.

        Ejemplos:
            "+57 3001234567" -> pais="+57", numero="3001234567"
            "+573001234567" -> pais="+57", numero="3001234567"
            "3001234567" -> pais="+57", numero="3001234567"
        """
        if not telefono:
            return TelefonoParseado(pais="+57", numero="", completo="")

        telefono = telefono.strip()

        for prefijo in sorted(cls.PREFIJOS_COMUNES.keys(), key=len, reverse=True):
            if telefono.startswith(prefijo):
                resto = telefono[len(prefijo) :].strip()
                if resto:
                    return TelefonoParseado(
                        pais=prefijo, numero=resto, completo=f"{prefijo} {resto}"
                    )

        if telefono.startswith("+"):
            parts = telefono.split(" ", 1)
            if len(parts) == 2:
                return TelefonoParseado(
                    pais=parts[0], numero=parts[1], completo=telefono
                )
            return TelefonoParseado(pais="+57", numero=telefono[1:], completo=telefono)

        return TelefonoParseado(pais="+57", numero=telefono, completo=f"+57 {telefono}")

    @classmethod
    def formatear_completo(cls, pais: str, numero: str) -> str:
        """Formatea país y número en un solo string."""
        if not numero:
            return ""
        pais = pais.strip() if pais else "+57"
        if not pais.startswith("+"):
            pais = f"+{pais}"
        return f"{pais} {numero.strip()}"

    @classmethod
    def prefill_desde_perfil(cls, telefono_perfil: str | None) -> dict:
        """
        Genera datos de prefill para formularios desde el teléfono del perfil.
        """
        if not telefono_perfil:
            return {"pais": "+57", "numero": ""}

        parsed = cls.parsear_telefono(telefono_perfil)
        return {"pais": parsed.pais, "numero": parsed.numero}

    @classmethod
    def sanitizar_numero(cls, numero: str) -> str:
        """Elimina espacios y guiones de un número."""
        if not numero:
            return ""
        return numero.replace(" ", "").replace("-", "")

    @classmethod
    def es_numero_valido(cls, telefono: str) -> bool:
        """Valida que el número sea un formato E.164 válido."""
        if not telefono or not isinstance(telefono, str):
            return False
        parsed = cls.parsear_telefono(telefono.strip())
        if not parsed.numero:
            return False
        # E.164: pais + 7-15 dígitos
        numero_limpio = parsed.numero.replace(" ", "").replace("-", "")
        return len(numero_limpio) >= 7 and numero_limpio.isdigit()

    @classmethod
    def normalizar_telefono(cls, telefono: str) -> str:
        """Retorna número en formato E.164 sin espacios (ej: +573001234567)."""
        if not telefono:
            return ""
        parsed = cls.parsear_telefono(telefono.strip())
        numero_limpio = parsed.numero.replace(" ", "").replace("-", "")
        return f"{parsed.pais}{numero_limpio}"

    @classmethod
    def obtener_codigo_pais(cls, telefono: str) -> str:
        """Extrae el código de país de un número E.164 (ej: +57)."""
        if not telefono:
            return "+57"
        return cls.parsear_telefono(telefono.strip()).pais
