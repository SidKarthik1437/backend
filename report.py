import sqlite3
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak
import pandas as pd

#set Passing marks here
threshold = 1

# Connect to SQLite database
conn = sqlite3.connect('db.sqlite3')  # Replace 'your_database.db' with the actual name of your SQLite database file
cursor = conn.cursor()

# Execute SQL query to retrieve data from the table
cursor.execute('SELECT id, student_id, studentMarks FROM api_result')  # Replace 'your_table' with the actual name of your table
data = cursor.fetchall()

# Close the database connection
conn.close()

# Create a DataFrame from the retrieved data
columns = ['id', 'student_id', 'studentMarks']
df = pd.DataFrame(data, columns=columns)

# Calculate FinalResult based on a threshold (adjust as needed)
c = ['id', 'student_id', 'studentMarks', 'Result']
df['FinalResult'] = df['studentMarks'].apply(lambda x: 'P' if x >= threshold else 'F')

# Rearrange table_data to include only specific columns
table_data = [c] + df[['id', 'student_id', 'studentMarks', 'FinalResult']].values.tolist()

# Create a PDF report
buffer = BytesIO()

# Set up the PDF document
pdf = SimpleDocTemplate(buffer, pagesize=letter)
pdf_title = "Student Marks Report"

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
with open('student_marks_report.pdf', 'wb') as f:
    f.write(buffer.read())
