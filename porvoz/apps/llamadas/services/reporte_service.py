"""
Servicio para generar reportes en CSV y PDF.
"""

from datetime import datetime, timedelta
from io import StringIO, BytesIO
import csv

from django.utils import timezone
from apps.llamadas.models import Llamada, RespuestaLlamada
from apps.pacientes.models import Paciente

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReporteService:
    """Genera reportes de adherencia y llamadas."""

    @staticmethod
    def obtener_datos_adherencia(paciente: Paciente, fecha_desde=None, fecha_hasta=None, medicamentos=None):
        """Obtiene datos de adherencia del paciente."""
        if not fecha_hasta:
            fecha_hasta = timezone.now().date()
        if not fecha_desde:
            fecha_desde = fecha_hasta - timedelta(days=30)

        if isinstance(fecha_desde, str):
            fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        if isinstance(fecha_hasta, str):
            fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()

        qs = Llamada.objects.filter(
            paciente=paciente,
            fecha_programada__date__gte=fecha_desde,
            fecha_programada__date__lte=fecha_hasta,
            estado__in=[Llamada.ESTADO_COMPLETADA, Llamada.ESTADO_FALLIDA]
        ).select_related('medicamento', 'paciente').prefetch_related('respuesta')

        if medicamentos:
            qs = qs.filter(medicamento_id__in=medicamentos)

        datos = {}
        for llamada in qs:
            med = llamada.medicamento
            if med not in datos:
                datos[med] = {'confirmadas': 0, 'no_confirmadas': 0, 'sin_respuesta': 0}

            try:
                respuesta = llamada.respuesta
            except RespuestaLlamada.DoesNotExist:
                respuesta = None

            if respuesta and respuesta.como_respondio == RespuestaLlamada.RESPUESTA_ATENDIDA:
                if respuesta.resultado == RespuestaLlamada.RESULTADO_CONFIRMADA:
                    datos[med]['confirmadas'] += 1
                else:
                    datos[med]['no_confirmadas'] += 1
            else:
                datos[med]['sin_respuesta'] += 1

        filas = []
        nombre_paciente = paciente.get_display_nombre()
        for med, stats in datos.items():
            total = stats['confirmadas'] + stats['no_confirmadas'] + stats['sin_respuesta']
            pct = (stats['confirmadas'] / total * 100) if total > 0 else 0
            filas.append({
                'paciente': nombre_paciente,
                'medicamento': med.nombre,
                'confirmadas': stats['confirmadas'],
                'no_confirmadas': stats['no_confirmadas'],
                'sin_respuesta': stats['sin_respuesta'],
                'total': total,
                'porcentaje': round(pct, 1)
            })

        return {
            'paciente': paciente.get_display_nombre(),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'filas': filas
        }

    @staticmethod
    def obtener_datos_incumplimientos(paciente: Paciente, fecha_desde=None, fecha_hasta=None, medicamentos=None):
        """Obtiene solo incumplimientos."""
        if not fecha_hasta:
            fecha_hasta = timezone.now().date()
        if not fecha_desde:
            fecha_desde = fecha_hasta - timedelta(days=30)

        if isinstance(fecha_desde, str):
            fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        if isinstance(fecha_hasta, str):
            fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()

        qs = Llamada.objects.filter(
            paciente=paciente,
            fecha_programada__date__gte=fecha_desde,
            fecha_programada__date__lte=fecha_hasta,
            estado__in=[Llamada.ESTADO_COMPLETADA, Llamada.ESTADO_FALLIDA]
        ).select_related('medicamento', 'paciente').prefetch_related('respuesta')

        if medicamentos:
            qs = qs.filter(medicamento_id__in=medicamentos)

        filas = []
        nombre_paciente = paciente.get_display_nombre()
        for llamada in qs:
            try:
                respuesta = llamada.respuesta
            except RespuestaLlamada.DoesNotExist:
                respuesta = None

            if respuesta and respuesta.como_respondio == RespuestaLlamada.RESPUESTA_ATENDIDA:
                if respuesta.resultado != RespuestaLlamada.RESULTADO_CONFIRMADA:
                    razon = 'Negativa' if respuesta.resultado == RespuestaLlamada.RESULTADO_NEGATIVA else (
                        'Aplazada' if respuesta.resultado == RespuestaLlamada.RESULTADO_DESPUES else 'Sin confirmar'
                    )
                    filas.append({
                        'paciente': nombre_paciente,
                        'fecha': llamada.fecha_programada.strftime("%d/%m/%Y %H:%M"),
                        'medicamento': llamada.medicamento.nombre,
                        'razon': razon,
                        'estado': 'Incumplimiento'
                    })
            else:
                filas.append({
                    'paciente': nombre_paciente,
                    'fecha': llamada.fecha_programada.strftime("%d/%m/%Y %H:%M"),
                    'medicamento': llamada.medicamento.nombre,
                    'razon': 'Sin respuesta',
                    'estado': 'No atendida'
                })

        return {
            'paciente': paciente.get_display_nombre(),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'filas': filas
        }

    @staticmethod
    def obtener_datos_auditoria(paciente: Paciente, fecha_desde=None, fecha_hasta=None, medicamentos=None):
        """Obtiene todas las llamadas con detalles completos."""
        if not fecha_hasta:
            fecha_hasta = timezone.now().date()
        if not fecha_desde:
            fecha_desde = fecha_hasta - timedelta(days=30)

        if isinstance(fecha_desde, str):
            fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        if isinstance(fecha_hasta, str):
            fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()

        qs = Llamada.objects.filter(
            paciente=paciente,
            fecha_programada__date__gte=fecha_desde,
            fecha_programada__date__lte=fecha_hasta
        ).select_related('medicamento', 'paciente').prefetch_related('respuesta')

        if medicamentos:
            qs = qs.filter(medicamento_id__in=medicamentos)

        filas = []
        nombre_paciente = paciente.get_display_nombre()
        for llamada in qs:
            try:
                respuesta = llamada.respuesta
            except RespuestaLlamada.DoesNotExist:
                respuesta = None

            respuesta_texto = 'No atendida'
            resultado = '—'
            transcripcion = '—'

            if respuesta:
                respuesta_texto = respuesta.get_como_respondio_display()
                resultado = respuesta.get_resultado_display() if respuesta.resultado else '—'
                if respuesta.transcripcion:
                    transcripcion = respuesta.transcripcion[:100]

            duracion = f"{llamada.duracion}s" if llamada.duracion else "—"

            filas.append({
                'paciente': nombre_paciente,
                'fecha': llamada.fecha_programada.strftime("%d/%m/%Y %H:%M"),
                'medicamento': llamada.medicamento.nombre if llamada.medicamento else '—',
                'estado': llamada.get_estado_display(),
                'respuesta': respuesta_texto,
                'resultado': resultado,
                'duracion': duracion,
                'transcripcion': transcripcion
            })

        return {
            'paciente': paciente.get_display_nombre(),
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'filas': filas
        }

    @staticmethod
    def generar_csv(tipo_reporte, datos):
        """Genera CSV a partir de datos."""
        output = StringIO()

        if tipo_reporte == 'adherencia':
            fieldnames = ['Paciente', 'Medicamento', 'Confirmadas', 'No Confirmadas', 'Sin Respuesta', 'Total', '% Adherencia']
        elif tipo_reporte == 'incumplimientos':
            fieldnames = ['Paciente', 'Fecha', 'Medicamento', 'Razón', 'Estado']
        else:  # auditoria
            fieldnames = ['Paciente', 'Fecha', 'Medicamento', 'Estado', 'Respuesta', 'Resultado', 'Duración', 'Transcripción']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for row in datos['filas']:
            if tipo_reporte == 'adherencia':
                writer.writerow({
                    'Paciente': row.get('paciente', ''),
                    'Medicamento': row.get('medicamento', ''),
                    'Confirmadas': row.get('confirmadas', 0),
                    'No Confirmadas': row.get('no_confirmadas', 0),
                    'Sin Respuesta': row.get('sin_respuesta', 0),
                    'Total': row.get('total', 0),
                    '% Adherencia': row.get('porcentaje', 0),
                })
            elif tipo_reporte == 'incumplimientos':
                writer.writerow({
                    'Paciente': row.get('paciente', ''),
                    'Fecha': row.get('fecha', ''),
                    'Medicamento': row.get('medicamento', ''),
                    'Razón': row.get('razon', ''),
                    'Estado': row.get('estado', ''),
                })
            else:  # auditoria
                writer.writerow({
                    'Paciente': row.get('paciente', ''),
                    'Fecha': row.get('fecha', ''),
                    'Medicamento': row.get('medicamento', ''),
                    'Estado': row.get('estado', ''),
                    'Respuesta': row.get('respuesta', ''),
                    'Resultado': row.get('resultado', ''),
                    'Duración': row.get('duracion', ''),
                    'Transcripción': row.get('transcripcion', ''),
                })

        # Retornar como bytes con BOM para Excel
        csv_content = output.getvalue()
        return csv_content.encode('utf-8-sig')

    @staticmethod
    def generar_pdf(tipo_reporte, datos):
        """Genera PDF a partir de datos."""
        if not REPORTLAB_AVAILABLE:
            # Fallback a CSV si reportlab no está disponible
            return ReporteService.generar_csv(tipo_reporte, datos)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12
        )

        # Título
        title = f"Reporte de {tipo_reporte.capitalize()}"
        elements.append(Paragraph(title, title_style))

        # Subtítulo con paciente y fechas
        paciente_info = f"Paciente: {datos.get('paciente', 'N/A')} | Período: {datos.get('fecha_desde', '')} a {datos.get('fecha_hasta', '')}"
        elements.append(Paragraph(paciente_info, subtitle_style))
        elements.append(Spacer(1, 0.2*inch))

        # Tabla de datos
        if datos['filas']:
            if tipo_reporte == 'adherencia':
                headers = ['Medicamento', 'Confirmadas', 'No Confirmadas', 'Sin Respuesta', 'Total', '% Adherencia']
            elif tipo_reporte == 'incumplimientos':
                headers = ['Fecha', 'Medicamento', 'Razón', 'Estado']
            else:  # auditoria
                headers = ['Fecha', 'Medicamento', 'Estado', 'Respuesta', 'Resultado', 'Duración', 'Transcripción']

            table_data = [headers]
            for row in datos['filas']:
                if tipo_reporte == 'adherencia':
                    table_data.append([
                        row.get('medicamento', ''),
                        str(row.get('confirmadas', '')),
                        str(row.get('no_confirmadas', '')),
                        str(row.get('sin_respuesta', '')),
                        str(row.get('total', '')),
                        f"{row.get('porcentaje', '')}%"
                    ])
                elif tipo_reporte == 'incumplimientos':
                    table_data.append([
                        row.get('fecha', ''),
                        row.get('medicamento', ''),
                        row.get('razon', ''),
                        row.get('estado', '')
                    ])
                else:  # auditoria
                    table_data.append([
                        row.get('fecha', ''),
                        row.get('medicamento', ''),
                        row.get('estado', ''),
                        row.get('respuesta', ''),
                        row.get('resultado', ''),
                        row.get('duracion', ''),
                        row.get('transcripcion', '—')
                    ])

            table = Table(table_data, colWidths=[1.2*inch]*len(headers))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay datos para mostrar.", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
