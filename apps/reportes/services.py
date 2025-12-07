import os
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFGeneratorService:
    """
    Servicio para generar PDFs de reportes de charlas
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos personalizados"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12
        )
    
    def generate_charla_report(self, charla):
        """
        Genera un PDF con el reporte de una charla
        
        Args:
            charla: Objeto Charla
        
        Returns:
            str: Path del archivo PDF generado
        """
        # Crear directorio si no existe
        report_dir = os.path.join(settings.MEDIA_ROOT, 'reportes')
        os.makedirs(report_dir, exist_ok=True)
        
        # Nombre del archivo
        filename = f'charla_{charla.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        filepath = os.path.join(report_dir, filename)
        
        # Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        # Título
        title = Paragraph(f"Reporte de Charla de Seguridad", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Información de la charla
        info_data = [
            ['Tema:', charla.tema],
            ['Fecha:', charla.fecha.strftime('%d/%m/%Y')],
            ['Hora:', charla.hora.strftime('%H:%M')],
            ['Supervisor:', charla.supervisor.get_full_name()],
            ['RUT Supervisor:', charla.supervisor.rut],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Lista de asistentes
        heading = Paragraph("Asistentes", self.heading_style)
        elements.append(heading)
        
        asistencias = charla.asistencias.select_related('usuario').all()
        
        if asistencias.exists():
            # Tabla de asistentes
            asistentes_data = [['N°', 'Nombre', 'RUT', 'Hora Firma']]
            
            for idx, asistencia in enumerate(asistencias, 1):
                asistentes_data.append([
                    str(idx),
                    asistencia.usuario.get_full_name(),
                    asistencia.usuario.rut,
                    asistencia.hora_firma.strftime('%H:%M:%S')
                ])
            
            asistentes_table = Table(asistentes_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            asistentes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(asistentes_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Resumen
            summary = Paragraph(
                f"<b>Total de asistentes:</b> {asistencias.count()}",
                self.styles['Normal']
            )
            elements.append(summary)
        else:
            no_asistentes = Paragraph(
                "No hay asistentes registrados para esta charla.",
                self.styles['Normal']
            )
            elements.append(no_asistentes)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer = Paragraph(
            f"Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
            ParagraphStyle('Footer', parent=self.styles['Normal'], 
                         fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(footer)
        
        # Construir PDF
        doc.build(elements)
        
        return f"{settings.MEDIA_URL}reportes/{filename}"