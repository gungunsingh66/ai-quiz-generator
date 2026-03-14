from fpdf import FPDF
import datetime


def generate_certificate(username, topic, score, total):

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 36)
    pdf.cell(0, 40, "Certificate of Achievement", align="C", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", size=20)
    pdf.cell(0, 15, "This certifies that", align="C", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 30)
    pdf.cell(0, 20, username, align="C", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", size=18)

    accuracy = round((score / total) * 100, 2)

    pdf.cell(
        0,
        15,
        f"has successfully completed the {topic} Quiz",
        align="C",
        ln=True,
    )

    pdf.cell(
        0,
        15,
        f"Score: {score}/{total}   |   Accuracy: {accuracy}%",
        align="C",
        ln=True,
    )

    pdf.ln(10)

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"Date: {date}", align="C", ln=True)

    file_name = "quiz_certificate.pdf"
    pdf.output(file_name)

    return file_name

