"""
Erzeugt PDF-Dateien aus JIRA-Issues
"""
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A6, landscape
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import html
import logging
from jira import JIRA
from jira.exceptions import JIRAError
from pathlib import Path
from . import ISSUE_TYPE2COLOR, EPIC_COLORS


def get_pdf_dir():
    """
    Verzeichnis zur Ablage der PDFs bestimmen
    :return: absoluter Pfad
    """
    pdf_dir = Path('./pdfs')

    try:
        pdf_dir.mkdir()
    except FileExistsError:
        pass

    return pdf_dir.resolve()


def delete_card(issue_key):
    pdf_file = get_pdf_dir() / '{}.pdf'.format(issue_key)
    pdf_file.unlink()
    logger = logging.getLogger(__name__)
    logger.debug('Deleted card %s', pdf_file)


def create_card(issue_key, issue_type, jira_config, debug=False):
    """
    Karte als PDF für einen Issue erzeugen
    :param issue_key: Key des Issue
    :param issue_type: Typ des Issue
    :param jira_config: Zugangsdaten für JIRA (URL, User, Passwort)
    :param debug: Debug-Modus (default: False)
    :return: absoluter Dateiname der erzeugten PDF-Datei
    """
    logger = logging.getLogger(__name__)

    if issue_type not in ISSUE_TYPE2COLOR:
        raise KeyError('Invalid issue type "{}"'.format(issue_type))

    filename = '{}/{}.pdf'.format(str(get_pdf_dir()), issue_key)

    canvas = Canvas(filename, pagesize=landscape(A6))
    height = A6[0]
    width = A6[1]

    epic_text = ['Epic: ']
    epic_color = None
    parent_text = ['Parent: ']

    if debug:
        logger.info('DEBUG-Mode')
        canvas.grid(range(0, 500, 50), range(0, 500, 50))
        issue_key = 'XXX-1337'
        issue_type = 'bug'
        summary = '<Bacon> ipsum dolor amet pork belly strip steak hamburger ' \
                  'turducken flank. Turkey bacon shankle short'
        epic_text = ['Epic: ', 'Test-Epic']
        epic_color = '#abcccc'
        parent_text = ['Parent: ', 'Test-Parent']
        labels = ['move_to_git', 'rewrite']
    else:
        jira = JIRA(jira_config['url'], basic_auth=(jira_config['user'], jira_config['password']))
        issue = jira.issue(issue_key)
        summary = issue.fields.summary
        labels = issue.fields.labels

        try:
            parent = jira.issue(issue.fields.parent.id)
            parent_text.append(parent.fields.summary)
        except AttributeError:
            parent = None

        try:
            if parent is None:
                epic = jira.issue(getattr(issue.fields, jira_config['epic_custom_field_key']))
            else:
                epic = jira.issue(getattr(parent.fields, jira_config['epic_custom_field_key']))

            epic_text.append(getattr(epic.fields, jira_config['epic_custom_field_name']))
            epic_color = EPIC_COLORS[getattr(epic.fields, jira_config['epic_custom_field_color'])]
        except JIRAError:
            pass

        canvas.setFillColor(ISSUE_TYPE2COLOR[issue_type])

    ticket_url = '{url}/browse/{issue_key}'.format(url=jira_config['url'], issue_key=issue_key)
    qr_dimensions = (50, 50)
    qr_coords = (20, height - 65)
    draw_qr_code(canvas, ticket_url, qr_coords, qr_dimensions)

    text = [
        {
            'text': ', '.join(labels),
            'size': 10,
            'x': width - 15,
            'y': 15,
            'align': 'right'
        },
        {
            'text': parent_text,
            'size': 18,
            'x': 20,
            'y': 28
        },
        {
            'text': epic_text,
            'size': 18,
            'x': 20,
            'y': 53,
            'backColor': epic_color
        },
        {
            'text': issue_key,
            'size': 28,
            'x': width - 20,
            'y': height - 40,
            'align': 'right'
        },
    ]

    draw_text(canvas, text)
    draw_summary_frame(canvas, summary, ISSUE_TYPE2COLOR[issue_type], debug)

    canvas.save()
    logger.info('Wrote PDF for %s: "%s" to %s', issue_key, summary, filename)
    return filename


def draw_summary_frame(canvas, summary, text_color, show_boundary):
    """
    Frame mit der Summary des Tickets zeichnen
    :param canvas:
    :param summary: Summary als Text
    :param text_color: Farbe für den Text
    :param show_boundary: Rahmen des Frames zeichnen?
    :return:
    """
    style = ParagraphStyle(name='Normal',
                           fontName='Helvetica',
                           fontSize=30,
                           leading=30,
                           alignment=TA_CENTER,
                           textColor=text_color)

    frame_width = 390
    frame_height = 170
    elements = list()
    paragraph = Paragraph(html.escape(summary), style)
    text_height = paragraph.wrap(frame_width, frame_height)[1]
    elements.append(paragraph)

    top_padding = (frame_height - text_height) / 2
    if top_padding <= 20:
        top_padding = 0

    frame = Frame(15, 70, frame_width, frame_height,
                  showBoundary=show_boundary,
                  topPadding=top_padding)
    frame.addFromList(elements, canvas)


def draw_text(canvas, text):
    """
    Beliebigen Text an beliebige Stellen zeichnen
    :param canvas:
    :param text: Liste mit Texten (Hashes)
    :return:
    """
    for value in text:
        canvas.setFont("Helvetica", value['size'])
        align = value.get('align')

        if align == 'right':
            canvas.drawRightString(value['x'], value['y'], value['text'])
        elif align == 'centered':
            canvas.drawCentredString(value['x'], value['y'], value['text'])
        else:
            canvas.drawString(value['x'], value['y'], value['text'][0])
            x_offset = value['x'] + canvas.stringWidth(value['text'][0])

            if value['text'][1:]:
                canvas.saveState()
                try:
                    canvas.setFillColor(value['backColor'])
                    canvas.roundRect(x=x_offset - 2, y=value['y'] - 5,
                                     width=canvas.stringWidth(value['text'][1]) + 5,
                                     height=22, radius=2, stroke=0, fill=1)
                    canvas.setFillColor(colors.white)
                except KeyError:
                    pass
                canvas.drawString(x_offset, value['y'], value['text'][1])
                canvas.restoreState()


def draw_qr_code(canvas, text, coords, dimensions):
    """
    QR-Code zeichnen
    :param canvas:
    :param text: Als QR-Code zu zeichnender Text
    :param coords: Koordinaten des QR-Codes
    :param dimensions: Größe des QR-Codes
    :return:
    """
    qr_code = qr.QrCodeWidget(text)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(0, 0, transform=[dimensions[0]/width, 0, 0, dimensions[1]/height, 0, 0])
    drawing.add(qr_code)
    renderPDF.draw(drawing, canvas, coords[0], coords[1])
