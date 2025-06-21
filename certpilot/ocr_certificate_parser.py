# ocr_certificate_parser.py

import google.generativeai as genai
from PIL import Image
import pytesseract
import cv2


class OCR_TEXT_DATA:

    @staticmethod
    def extract_text_from_image(image_path):
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    @staticmethod
    def extract_qr_data(image_path):
        image = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(image)
        return data if data else ""

    @staticmethod
    def extract_certificate_fields_gemini(text, api_key):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
You are an AI assistant. Analyze the OCR result from a certificate and extract the following fields only if they exist:

- Name
- Course
- Institute
- Website
- Certificate ID
- Certificate URL (if URL + ID, e.g., www.course.com/verify/123abc, treat it as Certificate URL)
- Issue Date

Return the output in this exact JSON format. If any field is not found, return it as an empty string ("").
 

{{
  "Name": "...",
  "Course": "...",
  "Institute": "...",
  "Website": "...",
  "Certificate ID": "...",
  "Certificate URL": "...",
  "Issue Date": "..."
}}

OCR TEXT:
{text}
"""
        response = model.generate_content(prompt)
        return response.text.strip()


def extract_certificate_data(image_path, gemini_api_key):
    print("🔍 Extracting OCR text...")
    ocr_text = OCR_TEXT_DATA.extract_text_from_image(image_path)

    print("📦 Extracting QR Code URL...")
    qr_url = OCR_TEXT_DATA.extract_qr_data(image_path)
    print(f"QR URL: {qr_url if qr_url else 'No QR code found'}")

    print("🤖 Extracting certificate fields using Gemini...")
    extracted_fields = OCR_TEXT_DATA.extract_certificate_fields_gemini(ocr_text, gemini_api_key)

    return {
        "QR URL": qr_url,
        "OCR Text": ocr_text,
        "Extracted Fields": extracted_fields
    }



   
