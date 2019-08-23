from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus.flowables import Spacer
from reportlab.lib import colors

from QA.models import Condicao

from datetime import date


class Printer:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize

    @staticmethod
    def header_and_footer(canvas, doc):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='sfm', alignment=TA_RIGHT, fontSize=10))
        canvas.saveState()
        header_data = [
            (Image("/opt/SFMRT/static/QA/images/ipo-logo.png", width=175, height=35, hAlign='LEFT'),
             Paragraph('Serviço de Física Médica', styles['sfm'])
             )
        ]
        header = Table(header_data)
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)
        footer = Paragraph(str(date.today()), styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    def to_pdf(self, registo):
        buffer = self.buffer
        condicoes_list = Condicao.objects.all()
        verifs_list = registo.verificacao.all()
        medidas = registo.medidas.all()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='test', frames=frame, onPage=self.header_and_footer)
        doc.addPageTemplates([template])
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='sfm', alignment=TA_CENTER, fontSize=14))
        styles.add(ParagraphStyle(name='report_date', alignment=TA_CENTER))
        elements = []
        elements.append(Spacer(0, 45))
        elements.append(Paragraph('Controlo Diário da Taxa de Dose', styles['Title']))
        elements.append(Spacer(0, 5))

        elements.append(Paragraph(str(registo.acelerador), styles['Title']))
        elements.append(Paragraph(str(registo.data), styles['report_date']))
        elements.append(Spacer(0, 45))

        elements.append(Paragraph("Condições de medida", styles['Heading3']))
        elements.append(Spacer(0, 10))
        condicoes = [['', 'Gantry (º)', 'Colimador (º)', 'DFP (cm)', 'Campo (cm)', 'Cone', 'PMMA (mm)', 'Dose (MU)']]
        for t in condicoes_list:
            condicoes.append([str(t.tipo), str(t.gantry), str(t.colimador),
             str(t.dfp), str(t.campo), str(t.cone), str(t.pmma),
             str(t.dose)])
        c = Table(condicoes)
        c.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('FONT', (0, 1), (0, -1), 'Helvetica-Bold'),
                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(c)
        elements.append(Spacer(0, 5))
        notes_style = styles['Italic']
        notes_style.alignment = TA_CENTER
        for c in condicoes_list:
            notas = str(c.notas)
            elements.append(Paragraph(notas, notes_style))
        elements.append(Spacer(0, 20))

        elements.append(Paragraph("Referências", styles['Heading3']))
        elements.append(Spacer(0, 10))
        first_row = ['Energia']
        second_row = ['+2%']
        third_row = ['']
        forth_row = ['-2%']
        for m in medidas:
            first_row.append(str(m.energia))
            second_row.append(str(round(m.referencia.get_tolerance_sup(), 3)))
            third_row.append(str(round(m.referencia.valor, 3)))
            forth_row.append(str(round(m.referencia.get_tolerance_inf(), 3)))
        referencias = [
            first_row,
            second_row,
            third_row,
            forth_row,
        ]
        r = Table(referencias)
        r.setStyle(TableStyle([('FONT', (0, 0), (-1, 1), 'Helvetica-Bold'),
                               ('FONT', (0, 1), (0, 1), 'Helvetica-Bold'),
                               ('FONT', (0, 2), (-1, -1), 'Helvetica-Bold'),
                               ('FONT', (0, 3), (0, 3), 'Helvetica-Bold'),
                               ('FONT', (1, 1), (-1, 1), 'Times-Italic'),
                               ('FONT', (1, 3), (-1, 3), 'Times-Italic'),
                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(r)
        elements.append(Spacer(0, 20))

        elements.append(Paragraph("Medidas", styles['Heading3']))
        elements.append(Spacer(0, 10))
        medidas = []
        medidas_header = []
        medidas_values = []
        for m in registo.medidas.all():
            medidas_header.append(m.energia)
            medidas_values.append(m.valor)
        medidas.append(medidas_header)
        medidas.append(medidas_values)
        m = Table(medidas)
        m.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(m)
        elements.append(Spacer(0, 20))

        elements.append(Paragraph("Verificações Mecânicas", styles['Heading3']))
        elements.append(Spacer(0, 10))
        verificacoes = [
            ['DFP', 'Lasers', 'Campo'],
            [str(verifs_list[0].dfp), str(verifs_list[0].lasers), str(verifs_list[0].campo)]
        ]
        v = Table(verificacoes)
        v.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        elements.append(v)
        elements.append(Paragraph("Realizado por: " + str(registo.autor), styles['Heading3']))

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
