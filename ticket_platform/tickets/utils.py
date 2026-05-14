import os
from io import BytesIO

import qrcode
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_qr_code(data):
    qr = qrcode.make(data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def generate_ticket_pdf(ticket):
    file_name = f"{ticket.code}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, "tickets", "pdfs", file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 100, "Ingresso do Evento")

    c.setFont("Helvetica", 14)
    c.drawString(100, height - 150, f"Código: {ticket.code}")

    if ticket.order and ticket.order.items.exists():
        item = ticket.order.items.first()
        event = item.ticket_type.event

        c.drawString(100, height - 200, f"Evento: {event.title}")
        c.drawString(100, height - 230, f"Local: {event.location}")
        c.drawString(
            100, height - 260, f'Data: {event.date.strftime("%d/%m/%Y %H:%M")}'
        )

    if ticket.qr_code:
        c.drawImage(ticket.qr_code.path, 100, height - 500, width=200, height=200)

    c.save()

    return file_path
