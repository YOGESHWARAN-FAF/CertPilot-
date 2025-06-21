# CertPilot-
🛡️ CertPilot – AI Certificate Verification System
✅ Say Goodbye to Fake Certificates
🔍 Verify. Analyze. Trust. All with AI.

🌟 What CertPilot Can Do
📥 1. Upload Certificate
Supports JPG, PNG, and PDF formats — ideal for scanned or digital documents.

🧾 2. OCR Extraction
Reads printed and scanned text using Tesseract OCR, even from noisy images.

🤖 3. Gemini 2.0 Field Extraction
Extracts fields like:

Name, Course, Institute, Website, Certificate ID, Issue Date
Using Google Gemini AI for high accuracy.

🔗 4. Dynamic Verification URL Detection
Detects and verifies from:

Embedded QR code

Certificate ID

Or via Google search fallback

🖼️ 5. Screenshot + Smart Cropping
Uses Playwright to screenshot pages and OpenCV to auto-crop the certificate section.

🧠 6. OCR + Gemini-Based Field Refinement
Runs field analysis again on the cropped area for improved accuracy.

🔁 7. AI Field Matching
Compares uploaded fields with AI-extracted values.
Handles OCR mismatches like B ↔ 8, 3 ↔ 2, etc.

🛡️ 8. Website Trust Check
✅ HTTPS/SSL presence

📅 Domain age via WHOIS

⚠️ Flags suspicious or fake websites

🌐 9. Social Media Validation
Scrapes links from website footer (LinkedIn, Instagram, Facebook)
Uses Gemini to evaluate the authenticity of those profiles.

🔍 10. LinkedIn Post Verifier
Analyzes public posts about the certificate issuer.
Flags fake hype or misleading claims.

⭐ 11. Review Sentiment Analysis
Uses SerpAPI + Gemini AI to summarize public reviews (Google, forums, etc.)

📊 12. Final Verdict + Trust Score
Gemini gives a smart, human-like conclusion:

✔️ Genuine

⚠️ Suspicious

❌ Likely Fake
With a 🔢 Trust Score (%) and explanation.

🧠 Why CertPilot Stands Out
Feature	Traditional Checker	✅ CertPilot
QR/ID validation	✅	✅
SSL & Domain Age Check	❌	✅
AI-Powered Field Extraction	❌	✅
Social Media Validation	❌	✅
Public Review Sentiment	❌	✅
Final Verdict by LLM	❌	✅

🎯 Why This Project Matters
✔️ A real-world tool for HR teams, recruiters, and training platforms
✔️ Helps prevent fraud, fake credentials, and online misinformation
✔️ Combines AI + Cybersecurity + Automation in one powerful solution
✔️ Perfect for hackathons, portfolios, and startup MVPs

⚙️ Tech Stack
Python, Flask

Playwright – Browser automation

OpenCV – Image cropping

Tesseract OCR – Text extraction

Google Gemini AI – Reasoning & field analysis

SerpAPI – Reviews & web trust scraping

BeautifulSoup – Web parsing

