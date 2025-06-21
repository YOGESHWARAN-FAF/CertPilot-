import os
import json
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from linkedin_verifier import verify_linkedin_posts
from ocr_certificate_parser import extract_certificate_data
from certificate_verifier import CertificateVerifier
from social_media_scraper import SocialMediaScraper
from certificate_processor import CertificateProcessor
from review_utils import ReviewScraperPlaywright, GeminiReviewAnalyzer
from website_check import WebsiteVerifier
from googlesearch import search
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# ========== Utility Functions ==========

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_website_trust_info(cert_url):
    return WebsiteVerifier.verify(cert_url) if cert_url else {}

def get_social_media_results(website):
    return SocialMediaScraper.scrape_social_and_check(website) if website else {}

def get_review_summary(cert_url, api_key):
    try:
        reviews = ReviewScraperPlaywright.scrape_reviews(cert_url) if cert_url else []
        if reviews:
            return GeminiReviewAnalyzer.summarize_and_rate_reviews(reviews, api_key)
        return None
    except Exception as e:
        print("❌ Review scraping failed:", e)
        return None

def compare_fields_with_gemini(ocr_text, extracted_fields, website_fields, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are an AI assistant verifying a digital certificate's authenticity.

1. The first input is raw OCR text extracted from a certificate image.
2. The second input is a set of fields extracted from that OCR text.
3. The third input is the set of fields extracted from the certificate verification website.

Your task:
- Compare the two sets of fields.
- Determine whether the certificate is real or fake based on how closely they match.
- Consider minor differences (like casing, spacing, or date formatting) as acceptable.
- If more than 50% of the fields mismatch or seem suspicious (name spelling, course mismatch, etc.), consider it fake.

Output ONLY valid JSON like this:
{{
  "Field_Matches": {{
    "Name": true,
    "Course": false,
    ...
  }},
  "Final_Verdict": "Real" / "Possibly Fake",
  "Reason": "Explain mismatches or issues found"
}}

Note: The certificate ID may be captured wrong by OCR (like 8==B or 3=2). Consider these as matches if they're structurally similar (90% match).
Also, ignore minor OCR errors like missing commas or spaces. If date is in different formats, consider it true.

OCR Text:
{ocr_text}

Extracted Fields from OCR:
{extracted_fields}

Fields from Verification Website:
{website_fields}
"""
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        result = json.loads(response_text)

        if not all(key in result for key in ['Field_Matches', 'Final_Verdict', 'Reason']):
            raise ValueError("Missing required fields in Gemini response")

        return result

    except Exception as e:
        print("❌ Gemini comparison error:", e)
        return {
            "Field_Matches": {},
            "Final_Verdict": "Error",
            "Reason": f"Comparison failed: {str(e)}"
        }

# ========== Main Logic ==========

def full_certificate_analysis(image_path, api_key):
    try:
        print("\n🔍 Extracting fields from uploaded certificate image...")
        extracted = extract_certificate_data(image_path, api_key)
        print("OCR QR URL:", extracted.get("QR URL"))
        print("OCR Extracted Fields:", extracted.get("Extracted Fields"))

        fields = extracted.get("Extracted Fields", {})
        if isinstance(fields, str):
            try:
                fields = re.sub(r"^```json\n|```$", "", fields.strip())
                fields = json.loads(fields)
            except Exception as e:
                print("❌ Error decoding extracted fields:", e)
                fields = {}

        cert_url = extracted.get("QR URL") or fields.get("Certificate URL")

        if not cert_url and fields.get("Website") and fields.get("Certificate ID"):
            cert_url = f"{fields['Website'].rstrip('/')}/student/certificate/{fields['Certificate ID']}"

        if not cert_url and fields.get("Certificate ID"):
            search_query = f'"{fields["Certificate ID"]}" certificate verification'
            print(f"🔍 Searching Google for certificate ID: {fields['Certificate ID']}")
            try:
                results = list(search(search_query, num_results=1))
                if results:
                    cert_url = results[0]
                    print(f"🌐 Found potential certificate URL via search: {cert_url}")
            except Exception as e:
                print(f"❌ Google Search failed: {e}")

        if not cert_url:
            print("❌ Could not determine certificate verification URL.")
            return {
                "error": "Could not determine certificate verification URL",
                "extracted_fields": fields
            }

        cert_processor = CertificateProcessor(api_key)

        print("\n📸 Scraping certificate page via screenshot OCR:")
        screenshot_path = cert_processor.capture_certificate_image(cert_url)
        cropped_path = cert_processor.crop_certificate_area(screenshot_path)
        cert_ocr_text = cert_processor.extract_text_from_image(cropped_path)
        fields_from_cert_page = cert_processor.extract_certificate_fields_gemini(cert_ocr_text)

        if isinstance(fields_from_cert_page, str):
            try:
                fields_from_cert_page = re.sub(r"^```json\n|```$", "", fields_from_cert_page.strip())
                fields_from_cert_page = json.loads(fields_from_cert_page)
            except Exception as e:
                print("❌ Error parsing fields from certificate page:", e)
                fields_from_cert_page = {}

        print("Fields from Certificate Page OCR:", json.dumps(fields_from_cert_page, indent=2))

        print("\n🤖 Comparing OCR vs Certificate Page Fields using Gemini...")
        comparison_result = compare_fields_with_gemini(
            cert_ocr_text,
            json.dumps(fields, indent=2),
            json.dumps(fields_from_cert_page, indent=2),
            api_key
        )
        print("Comparison result:", comparison_result)

        website = fields.get("Website", "")
        domain = website.replace("https://", "").replace("http://", "").split("/")[0] if website else ""

        trust_info, social_result, review_summary, linkedin_results = {}, {}, None, []

        # 🚀 Parallel processing
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_trust = executor.submit(get_website_trust_info, cert_url)
            future_social = executor.submit(get_social_media_results, website)
            future_reviews = executor.submit(get_review_summary, cert_url, api_key)

            trust_info = future_trust.result()
            social_result = future_social.result()
            review_summary = future_reviews.result()

        if domain:
            print("\n🔍 Verifying LinkedIn credibility via posts...")
            linkedin_results = verify_linkedin_posts(domain)

        return {
            "extracted_fields": fields,
            "website_fields": fields_from_cert_page,
            "comparison_result": comparison_result,
            "website_trust": trust_info,
            "social_media": social_result,
            "linkedin_results": linkedin_results,
            "review_summary": review_summary,
            "certificate_url": cert_url
        }

    except Exception as e:
        print("❌ Error in full certificate analysis:", e)
        return {
            "error": str(e),
            "message": "Certificate analysis failed"
        }

# ========== API Routes ==========

def safe_jsonify(data):
    try:
        def convert(value):
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, list):
                return [convert(v) for v in value]
            if isinstance(value, bytes):
                return value.decode()
            return value
        return jsonify(convert(data))
    except Exception as e:
        return jsonify({"error": "Serialization failed", "details": str(e)})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workflow')
def workflow():
    return render_template('workflow.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            api_key = "# Replace with your Gemini API key"  # Replace with your Gemini API key
            result = full_certificate_analysis(filepath, api_key)

            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print("❌ Error removing temporary file:", e)

            return safe_jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
