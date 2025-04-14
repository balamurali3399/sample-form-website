from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pdfkit
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

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
    5,5,  # Questions 1–5: Rating 1–5
    10,  # 6–10: Rating 1–10
    5,5,  # 11–15
    10,10,
    5,
    10,10,10,
    5,5,
    10,10,10,10,10,
    10,
    5,# 16–21
]

@app.route('/')
def index():
    return render_template('index.html', questions=questions, rating_ranges=rating_ranges)

@app.route('/submit', methods=['POST'])
def submit():
    answers = []
    ratings = []
    images = {}
    department = request.form.get("department", "")
    date = request.form.get("date", "")
    email = request.form.get("email", "")

    for i in range(len(questions)):
        answers.append(request.form.get(f'answer_{i}', ''))
        ratings.append(request.form.get(f'rating_{i}', ''))
        image_files = request.files.getlist(f'image_{i}')
        saved_images = []

        for file in image_files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_images.append(filename)

        images[f'q{i}'] = saved_images

    return render_template(
        'result.html',
        questions=questions,
        answers=answers,
        ratings=ratings,
        images=images,
        department=department,
        date=date,
        email=email
    )

@app.route('/download', methods=['POST'])
def download_pdf():
    answers = json.loads(request.form['answers'])
    ratings = json.loads(request.form['ratings'])
    images = json.loads(request.form['images'])
    department = request.form.get('department', '')
    date = request.form.get('date', '')
    email = request.form.get('email', '')

    rendered_html = render_template(
        'result.html',
        questions=questions,
        answers=answers,
        ratings=ratings,
        images=images,
        department=department,
        date=date,
        email=email
    )

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audit_report.pdf')
    pdfkit.from_string(rendered_html, pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

