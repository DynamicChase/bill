from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

app = Flask(__name__)
os.makedirs("invoices", exist_ok=True)

# Company GSTIN
GSTIN_NUMBER = "27XXXXXXXXXX"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_invoice():
    # ===== RECEIVER DETAILS =====
    receiver_name = request.form["receiver_name"]
    receiver_company = request.form.get("receiver_company", "")
    receiver_address = request.form.get("receiver_address", "")
    receiver_gstin = request.form.get("receiver_gstin", "")

    # ===== CLIENT DETAILS =====
    client_name = request.form["client_name"]
    phone = request.form["phone"]

    # ===== ITEMS =====
    items = request.form.getlist("item[]")
    rates = request.form.getlist("rate[]")
    days = request.form.getlist("days[]")

    # ===== FILE SETUP =====
    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    file_path = f"invoices/{invoice_no}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 50

    # ===== HEADER =====
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Anadih Enterprises")
    y -= 22

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"GSTIN: {GSTIN_NUMBER}")
    y -= 18

    c.drawString(50, y, "Shooting Lights Rental Invoice")
    y -= 15
    c.line(50, y, width - 50, y)
    y -= 25

    # ===== INVOICE INFO =====
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Invoice No: {invoice_no}")
    c.drawString(350, y, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
    y -= 20

    # ===== CLIENT INFO =====
    c.drawString(50, y, f"Prepared By: {client_name}")
    c.drawString(350, y, f"Phone: {phone}")
    y -= 25

    # ===== RECEIVER INFO =====
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Bill To:")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Name: {receiver_name}")
    y -= 14
    if receiver_company:
        c.drawString(50, y, f"Company: {receiver_company}")
        y -= 14
    if receiver_address:
        c.drawString(50, y, f"Address: {receiver_address}")
        y -= 14
    if receiver_gstin:
        c.drawString(50, y, f"GSTIN: {receiver_gstin}")
        y -= 14

    y -= 10  # space before items table

    # ===== ITEMS TABLE HEADER =====
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(260, y, "Rate/Day (INR)")
    c.drawString(360, y, "Days")
    c.drawString(430, y, "Amount (INR)")
    y -= 12
    c.line(50, y, width - 50, y)
    y -= 18

    # ===== ITEMS TABLE CONTENT =====
    c.setFont("Helvetica", 11)
    subtotal = 0.0

    for i in range(len(items)):
        amount = float(rates[i]) * int(days[i])
        subtotal += amount

        c.drawString(50, y, items[i])
        c.drawString(260, y, f"INR {float(rates[i]):.2f}")
        c.drawString(360, y, days[i])
        c.drawString(430, y, f"INR {amount:.2f}")
        y -= 18

    # ===== TOTALS =====
    gst = subtotal * 0.18
    total = subtotal + gst

    y -= 20
    c.drawRightString(width - 50, y, f"Subtotal: INR {subtotal:.2f}")
    y -= 18
    c.drawRightString(width - 50, y, f"GST @18%: INR {gst:.2f}")
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 50, y, f"TOTAL AMOUNT: INR {total:.2f}")

    # ===== BANK DETAILS =====
    y -= 45
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Bank Details")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Account Name: Anadih Enterprises")
    y -= 14
    c.drawString(50, y, "Bank Name: HDFC Bank")
    y -= 14
    c.drawString(50, y, "Account Number: 1234567890")
    y -= 14
    c.drawString(50, y, "IFSC Code: HDFC0001234")

    # ===== FOOTER =====
    c.setFont("Helvetica", 9)
    c.drawString(50, 70, "This is a computer-generated invoice.")
    c.drawString(50, 55, "Thank you for choosing Anadih Enterprises.")

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
