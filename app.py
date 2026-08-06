import os
import fitz
import cv2
import numpy as np
import pytesseract
import imutils
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

# Set Tesseract path (Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = MongoClient("mongodb://localhost:27017/")
db = client["ocr_app"]
users_col = db["users"]

def detect_text_regions(image_path):
    image = cv2.imread(image_path)
    orig = image.copy()
    (H, W) = image.shape[:2]

    net = cv2.dnn.readNet("frozen_east_text_detection.pb")

    newW, newH = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)

    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    blob = cv2.dnn.blobFromImage(
        image, 1.0, (W, H),
        (123.68, 116.78, 103.94),
        swapRB=True, crop=False
    )

    net.setInput(blob)
    (scores, geometry) = net.forward(
        ["feature_fusion/Conv_7/Sigmoid",
         "feature_fusion/concat_3"]
    )

    rects = []
    confidences = []

    for y in range(scores.shape[2]):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(scores.shape[3]):
            if scoresData[x] < 0.5:
                continue

            offsetX = x * 4.0
            offsetY = y * 4.0

            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(float(scoresData[x]))

    indices = cv2.dnn.NMSBoxes(rects, confidences, 0.5, 0.4)

    results = []

    if len(indices) > 0:
        for i in indices.flatten():
            (startX, startY, endX, endY) = rects[i]

            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)

            roi = orig[startY:endY, startX:endX]
            results.append(roi)

    return results

def extract_text(file_path):
    extracted_text = ""

    # If PDF
    if file_path.lower().endswith('.pdf'):
        pdf_file = fitz.open(file_path)

        for page_num in range(pdf_file.page_count):
            page = pdf_file.load_page(page_num)

            # Try direct text extraction
            text = page.get_text("text")

            if text.strip():
                extracted_text += f"\n\n=== Page {page_num + 1} (Digital Text) ===\n{text}"
            else:
                extracted_text += f"\n\n=== Page {page_num + 1} (Scanned OCR) ===\n"

                pix = page.get_pixmap(dpi=300)
                img_data = np.frombuffer(pix.samples, dtype=np.uint8)
                img = img_data.reshape(pix.height, pix.width, pix.n)

                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                thresh = cv2.threshold(
                    gray, 0, 255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )[1]

                ocr_result = pytesseract.image_to_string(thresh)
                extracted_text += ocr_result

        pdf_file.close()

    # If Image
    else:
        image = cv2.imread(file_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        extracted_text = pytesseract.image_to_string(thresh)

    return extracted_text



@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if users_col.find_one({"username": username}):
            flash("User already exists.")
            return redirect(url_for('register'))

        users_col.insert_one({"username": username, "password": password})
        flash("Account created.")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_col.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('upload'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    user = users_col.find_one({"username": username})
    ocr_text = ""
    previous_files = user.get("extracted_files", [])

    if request.method == 'POST':
        file = request.files['file']

        allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp')

        if file and file.filename.lower().endswith(allowed_extensions):
            pdf_name = file.filename
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_name)
            file.save(pdf_path)

            ocr_text = extract_text(pdf_path)

            extracted_entry = {
                "filename": pdf_name,
                "content": ocr_text
            }

            users_col.update_one(
                {"username": username},
                {"$push": {"extracted_files": extracted_entry}}
            )

            previous_files.append(extracted_entry)
        else:
            flash("Upload a valid PDF.")

    return render_template(
        'index.html',
        username=username,
        ocr_text=ocr_text,
        previous_files=previous_files
    )


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
