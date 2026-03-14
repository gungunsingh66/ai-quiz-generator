from fpdf import FPDF
import datetime


def generate_pdf(username, topic, difficulty, score, total):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=16)

    pdf.cell(200, 10, txt="AI Quiz Report", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"User: {username}", ln=True)
    pdf.cell(200, 10, txt=f"Topic: {topic}", ln=True)
    pdf.cell(200, 10, txt=f"Difficulty: {difficulty}", ln=True)

    pdf.cell(200, 10, txt=f"Score: {score}/{total}", ln=True)

    accuracy = round((score / total) * 100, 2)
    pdf.cell(200, 10, txt=f"Accuracy: {accuracy}%", ln=True)

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(200, 10, txt=f"Date: {date}", ln=True)

    file_name = "quiz_report.pdf"
    pdf.output(file_name)

    return file_name