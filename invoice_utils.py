
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_invoice(
    billing_id,
    username,
    plan_name,
    price,
    start_date,
    end_date,
    transaction_id
):
    invoice_dir = Path("media/invoices")
    invoice_dir.mkdir(parents=True, exist_ok=True)

    file_path = invoice_dir / f"invoice_{billing_id}.pdf"

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 60, "BLOG SUBSCRIPTION INVOICE")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 120, f"Invoice ID: {billing_id}")
    pdf.drawString(50, height - 150, f"Customer: {username}")
    pdf.drawString(50, height - 180, f"Plan: {plan_name}")
    pdf.drawString(50, height - 210, f"Price: Rs. {price}")
    pdf.drawString(50, height - 240, f"Start Date: {start_date}")
    pdf.drawString(50, height - 270, f"End Date: {end_date}")
    pdf.drawString(50, height - 300, f"Transaction ID: {transaction_id}")

    pdf.drawString(
        50,
        height - 360,
        "Thank you for subscribing!"
    )

    pdf.save()

    return f"/media/invoices/invoice_{billing_id}.pdf"