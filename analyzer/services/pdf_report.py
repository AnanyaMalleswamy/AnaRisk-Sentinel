from io import BytesIO

from reportlab.pdfgen import canvas


def generate_pdf():
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setTitle("Investigation Report")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, "Banking Transaction Investigation Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, "PDF generation is working!")
    pdf.drawString(50, 730, "Customer: TEST")
    pdf.drawString(50, 700, "Status: TEST")

    pdf.save()

    buffer.seek(0)
    return buffer