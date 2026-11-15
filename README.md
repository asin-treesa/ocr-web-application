# OCR Web Application

A Python and Flask-based web application that extracts editable text from scanned PDF documents and images using Optical Character Recognition (OCR).

## Overview

This project automates text extraction from scanned documents, reducing manual effort and making document content searchable and reusable. It integrates OCR, image preprocessing, user authentication and database management into a single web application.

## Features

- User registration and login with password hashing.
- Upload PDF and supported image files.
- Extract text from digital and scanned PDFs.
- Image preprocessing using OpenCV.
- OCR-based text recognition using Tesseract.
- Multi-page PDF processing.
- Store and retrieve extraction history using MongoDB.
- Flask session management.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | Web framework |
| MongoDB | Database |
| PyMuPDF | PDF processing |
| OpenCV | Image preprocessing |
| Tesseract OCR | Text recognition |
| PyTesseract | OCR integration |
| Werkzeug | Password hashing |
| HTML, CSS, JavaScript | Frontend |

## Workflow

1. User registers or logs into the application.
2. Uploads a PDF or image.
3. PyMuPDF checks for directly extractable PDF text.
4. Scanned pages are converted into images.
5. OpenCV preprocesses images using grayscale conversion, Gaussian blur and thresholding.
6. Tesseract extracts text from the processed images.
7. Extracted results are stored in MongoDB and displayed to the user.

## Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/asin-treesa/image-processing.git
cd image-processing
```

**2. Create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install Flask PyMuPDF opencv-python numpy pytesseract pymongo imutils
```

**4. Install Tesseract OCR**

Install Tesseract OCR and configure its executable path in `app.py`.

**5. Start MongoDB**

Ensure your local MongoDB server is running.

**6. Run the application**

```bash
python app.py
```

Open `http://127.0.0.1:5000/` in your browser.

## Future Improvements

- Cloud deployment and MongoDB Atlas integration.
- Multi-language OCR support.
- Advanced image preprocessing.
- Asynchronous processing for large documents.
- Enhanced security and performance optimization.

## Project Information

- **Internship Organization:** Centre for Development of Imaging Technology (CDIT), Kerala
- **Duration:** 08 May 2025 – 07 June 2025
- **Author:** Asin Treesa Rose
- **GitHub:** https://github.com/asin-treesa/image-processing
