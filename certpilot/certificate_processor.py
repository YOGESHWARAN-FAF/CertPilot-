import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import json
import time


class CertificateProcessor:
    def __init__(self, gemini_api_key=None):
        self.api_key = gemini_api_key
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

    @staticmethod
    def capture_certificate_image(url, output_folder="screenshots", file_name="certificate.png"):
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, file_name)
        if not url.startswith("http"):
            url = "https://" + url

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 720})
            page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
            try:
                print("\U0001F310 Opening URL:", url)
                page.goto(url, wait_until="load", timeout=20000)
                page.evaluate("document.body.style.zoom='150%'")
                page.wait_for_timeout(1000)
                page.screenshot(path=output_path, full_page=True)
                print(f"📸 Screenshot saved to {output_path}")
            except Exception as e:
                print("❌ Screenshot error:", e)
            finally:
                browser.close()
        return output_path

    @staticmethod
    def crop_certificate_area(image_path, cropped_output="screenshots/cropped_certificate.png"):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 30, 100)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in sorted(contours, key=cv2.contourArea, reverse=True):
            x, y, w, h = cv2.boundingRect(c)
            area, ratio = w * h, w / float(h)
            if area > 150000 and 1.2 < ratio < 1.8:
                cropped = image[y:y + h, x:x + w]
                cv2.imwrite(cropped_output, cropped)
                print(f"✂️ Cropped to {cropped_output}")
                return cropped_output

        print("⚠️ Cropping failed, using full image.")
        return image_path

    @staticmethod
    def preprocess_image_for_ocr(image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        resized = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(resized, -1, sharpen_kernel)
        _, thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_path = image_path.replace(".png", "_processed.png")
        cv2.imwrite(processed_path, thresh)
        return processed_path

    @staticmethod
    def extract_text_from_image(image_path):
        try:
            processed_path = CertificateProcessor.preprocess_image_for_ocr(image_path)
            image = Image.open(processed_path)
            config = "--psm 3 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:/.-"
            return pytesseract.image_to_string(image, config=config).strip()
        except Exception as e:
            print("❌ OCR error:", e)
            return ""

    def extract_certificate_fields_gemini(self, text):
        try:
            prompt = f"""
Extract the following fields from the certificate OCR text and return valid JSON:
- Name
- Course
- Institute
- Website
- Certificate ID
- Certificate URL
- Issue Date
If not found, use empty string. Format strictly as JSON with double quotes.

Text:
{text}
"""
            start = time.time()
            response = self.gemini_model.generate_content(prompt)
            print(f"⏱️ Gemini extraction took {round(time.time()-start,2)}s")
            return response.text.strip()
        except Exception as e:
            print("❌ Gemini error:", e)
            return "{}"

    def process_certificate(self, url):
        with ThreadPoolExecutor(max_workers=4) as executor:
            screenshot_future = executor.submit(self.capture_certificate_image, url)
            screenshot_path = screenshot_future.result()

            crop_future = executor.submit(self.crop_certificate_area, screenshot_path)
            cropped_path = crop_future.result()

            ocr_future = executor.submit(self.extract_text_from_image, cropped_path)
            ocr_text = ocr_future.result()

            gemini_future = executor.submit(self.extract_certificate_fields_gemini, ocr_text)
            gemini_json = gemini_future.result()

        
        print("\n✅ Final Extracted Fields:")
        try:
          gemini_clean = gemini_json.replace("```json", "").replace("```", "").strip()
          parsed = json.loads(gemini_clean)
          print(json.dumps(parsed, indent=2))
        except Exception as e:
            print("❌ Failed to parse JSON:", e)
            print(gemini_json)



