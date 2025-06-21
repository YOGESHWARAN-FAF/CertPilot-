🛡️ CertPilot – AI Certificate Verification System
✅ Say Goodbye to Fake Certificates
🔍 Verify. Analyze. Trust. All with AI.

🌟 What CertPilot Can Do
📥 1. Upload Certificate
Supports JPG, PNG formats — ideal for scanned or digital documents.

🧾 2. OCR Extraction
Reads printed and scanned text using Tesseract OCR, even from noisy or low-quality images.

🤖 3. Gemini 2.0 Field Extraction
Uses Google Gemini AI to extract key fields like:

Name, Course, Institute, Website, Certificate ID, Issue Date

🔗 4. Dynamic Verification URL Detection
Detects and verifies certificate source from:

Embedded QR Code

Certificate ID

Or intelligent Google Search fallback

🖼️ 5. Screenshot + Smart Cropping
Captures full certificate page using Playwright and crops certificate section with OpenCV.

🧠 6. OCR + Gemini-Based Field Refinement
Runs a second OCR + AI pass on the cropped region for highly accurate field detection.

🔁 7. AI Field Matching
Compares uploaded values vs extracted fields.
Handles minor OCR mismatches like B ↔ 8, 3 ↔ 2, etc.

🛡️ 8. Website Trust Check
✅ Checks SSL/HTTPS

📅 Fetches domain age via WHOIS

⚠️ Flags phishing or suspicious domains

🌐 9. Social Media Scraper
Scrapes footer links (LinkedIn, Facebook, Instagram) from issuer website.
Uses Gemini AI to evaluate authenticity of profiles.

🔍 10. LinkedIn Post Verifier
Analyzes public posts related to the issuer and flags fake claims using Gemini.

⭐ 11. Review Sentiment Analysis
Scrapes review platforms via SerpAPI and uses Gemini for summary-level analysis.

📊 12. Final Verdict + Trust Score
AI gives a smart verdict:

✔️ Genuine

⚠️ Suspicious

❌ Likely Fake
Includes a human-readable explanation and Trust Score (%).

🧠 Why CertPilot Stands Out
🔍 Feature	Traditional Verifier	✅ CertPilot
QR/ID Validation	✅	✅
SSL & Domain Trust Check	❌	✅
AI-Powered Field Extraction	❌	✅
Social Media Verification	❌	✅
Review Sentiment Analysis	❌	✅
AI-Based Final Verdict	❌	✅

🎯 Why This Project Matters
✔️ A real-world tool for HR teams, recruiters, colleges, and platforms
✔️ Stops the spread of fake credentials and digital misinformation
✔️ Combines AI + Cybersecurity + Automation into one powerful solution
✔️ Hackathon-ready, portfolio-worthy, and startup-scalable

⚙️ Tech Stack
Python, Flask

Playwright – for automated browser screenshots

OpenCV – for visual certificate cropping

Tesseract OCR – for text recognition

Google Gemini AI – for reasoning and field verification

SerpAPI – for company review scraping

BeautifulSoup – for HTML parsing

