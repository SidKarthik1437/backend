
import sqlite3
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak
import pandas as pd

def generate_report(exam_id):
    # Connect to SQLite database
    conn = sqlite3.connect('db.sqlite3')  # Replace 'your_database.db' with the actual name of your SQLite database file
    cursor = conn.cursor()

    # Execute SQL query to retrieve data from the table for a specific exam_id
    cursor.execute(f'SELECT student_id, studentMarks FROM api_result WHERE exam_id = {exam_id}')
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Create a DataFrame from the retrieved data
    columns = ['student_id', 'studentMarks']
    df = pd.DataFrame(data, columns=columns)

    # Create a PDF report
    buffer = BytesIO()

    # Set up the PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    pdf_title = f"Student Marks Report - Exam ID: {exam_id}"

    # Rearrange table_data to include only specific columns and add column headings
    table_data = [['Sl.no', 'Student ID', 'Marks']] + [[i+1, row['student_id'], row['studentMarks']] for i, row in df.iterrows()]

    # Define the style of the table
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    # Create the table and apply the style
    table = Table(table_data, style=style)

    # Add the table to the PDF
    pdf_title += " - Page 1"
    pdf.build([table])

    # Save the PDF
    buffer.seek(0)
    with open(f'student_marks_report_exam_{exam_id}.pdf', 'wb') as f:
        f.write(buffer.read())

# Example usage:
generate_report(3)  # Replace 1 with the desired exam_id
