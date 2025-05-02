import os
import base64
from flask import Flask, render_template, request,session,send_file
from werkzeug.utils import secure_filename
import pdfkit
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/uploads'
PDF_FOLDER = 'static/pdfs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

if os.name == 'nt':  # Windows
    path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
else:  # Linux (e.g., PythonAnywhere)
    path_to_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # or another path if you uploaded it
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

questions = [
    "Has unwanted items found kept here and there",
    "Has Red tag area defined",
    "Listing of Red tag items Department wise",
    "Has broom, wiper, cleaning items found lying here and there",
    "Has any tappa,trolley etc. broken and kept in the area",
    "Has notices/instructions displayed and updated(current year) properly on boards",
    "Has Aisle and other area of production marking been there",
    "Has location been properly marked/fixed to keep required items with Vinyl sticker/Sign boards",
    "Has railing been provided to prevent machines and walls from hit of any movable trolley",
    "Has electrical safety been considered",
    "Has machines, Almira, trolleys, crate, electrical panel been cleaned (In and Around)",
    "Has walls and ceiling cleaned",
    "Has floor free from any spillage (oil, water ; Shop floor, Washroom, Drinking point)",
    "All DUCTS/TRUSS cleaned",
    "Cleaning schedule of each section there and followed",
    "Color codification of all pipelines (egs. Water, oil, steam blow room/card duct etc.)",
    "Has Fire cylinders, Hose reels, Fire windows as per standard",
    "Self audit in practice by area owner. Minimum five observations must be there on the audit sheet.",
    "5S Story Board available & updated",
    "5S Awareness (Operators)",
    "5S Training given at shop floor (Operators)"
]

rating_ranges = [
    10,
    5, 5,
    10,
    5, 5,
    10, 10,
    5,
    10, 10, 10,
    5, 5,
    10, 10, 10, 10, 10,
    10,
    5,
]

@app.route('/', methods=['GET', 'POST'])
def index():
    answers = session.get('answers', [''] * len(questions))
    ratings = session.get('ratings', [''] * len(questions))
    department = session.get('department', '')
    date = session.get('date', '')
    email = session.get('email', '')
    images = session.get('images', {})

    if request.method == 'POST':
        department = request.form.get("department", department)
        date = request.form.get("date", date)
        email = request.form.get("email", email)

        return render_template(
            'index.html',
            questions=questions,
            rating_ranges=rating_ranges,
            ratings=ratings,
            answers=answers,
            images=images,
            department=department,
            email=email,
            date=date
        )
    return render_template('index.html', questions=questions, rating_ranges=rating_ranges, ratings=[], answers=[], images={}, department='', email='', date=datetime.today().strftime('%Y-%m-%d'))

@app.route('/submit', methods=['POST'])
def submit():
    answers = []
    ratings = []
    uploaded_images = {}

    for i, question in enumerate(questions):
        answers.append(request.form.get(f'answer_{i}', ''))
        ratings.append(request.form.get(f'rating_{i}', ''))

        uploaded_images[f'q{i}'] = []
        files = request.files.getlist(f'image_{i}')
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                uploaded_images[f'q{i}'].append(filename)

    department = request.form.get('department', '')
    email = request.form.get('email', '')
    date = request.form.get('date', '')

    return render_template(
        'result.html',
        questions=questions,
        ratings=ratings,
        answers=answers,
        images=uploaded_images,
        department=department,
        email=email,
        date=date
    )

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    department = request.form['department']
    email = request.form['email']
    date = request.form['date']
    ratings = json.loads(request.form['ratings'])
    answers = json.loads(request.form['answers'])
    images = json.loads(request.form['images'])

    # Convert images to base64 and prepare them for embedding
    base64_images = {}
    for key in images:
        base64_images[key] = []
        for img_filename in images[key]:
            img_path = os.path.join('static', 'uploads', img_filename)
            print(f"Image path: {img_path}")
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    base64_images[key].append(encoded)
                
            else:
             print(f"Error: {img_path} does not exist")

            

    # Render the HTML template for PDF generation
    rendered_html = render_template('pdf_template.html',
                                    department=department,
                                    email=email,
                                    date=date,
                                    questions=questions,
                                    ratings=ratings,
                                    answers=answers,
                                    images=images,
                                    base64_images=base64_images,)

    # wkhtmltopdf options to allow local file access
    options = {
        'enable-local-file-access': True  # Allow wkhtmltopdf to access local static files
    }

    # Generate PDF from rendered HTML
    pdf_data = pdfkit.from_string(rendered_html, False, options=options, configuration=config)

    # Save PDF to a directory named after the email
    output_dir = os.path.join('static', 'pdfs', email)
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{date}_5S_Audit.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
