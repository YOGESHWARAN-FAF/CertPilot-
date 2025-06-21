import requests
from bs4 import BeautifulSoup
import webbrowser

class CertificateVerifier:

    @staticmethod
    def verify_certificate(data: dict) -> str:
        qr_url = data.get("QR URL", "").strip()
        cert_url = data.get("Certificate URL", "").strip()
        website = data.get("Website", "").replace("https://", "").replace("http://", "").strip("/")
        cert_id = data.get("Certificate ID", "").strip()

        if qr_url:
            print("🔍 Found QR URL. Verifying directly...")
            if CertificateVerifier.open_and_check_url(qr_url):
                return f"✅ Certificate is original (via QR URL): {qr_url}"

        if cert_url:
            print("🔍 Found direct Certificate URL. Verifying...")
            if CertificateVerifier.open_and_check_url(cert_url):
                return f"✅ Certificate is original (via Certificate URL): {cert_url}"

        if website and cert_id:
            print("🔍 Generating URL from website and certificate ID...")
            return CertificateVerifier.guess_verification_url(website, cert_id)

        return "❌ Unable to verify: missing valid URL, website, or certificate ID."

    @staticmethod
    def open_and_check_url(url: str) -> bool:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and "certificate" in res.text.lower():
                webbrowser.open(url)
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def guess_verification_url(website: str, cert_id: str) -> str:
        domain_patterns = {
            "coursera.org": [f"https://www.coursera.org/verify/{cert_id}"],
            "edx.org": [f"https://credentials.edx.org/credentials/{cert_id}/"],
            "datacamp.com": [f"https://www.datacamp.com/statement-of-accomplishment/{cert_id}"],
            "greatlearning.in": [f"https://verify.greatlearning.in/certificate/{cert_id}"],
            "mindluster.com": [f"https://www.mindluster.com/student/certificate/{cert_id}"],
            "alison.com": [f"https://alison.com/certification/check/{cert_id}"],
            "simplilearn.com": [f"https://certificates.simplilearn.com/verify/{cert_id}"],
            "default": [
                f"https://{website}/certificate/{cert_id}",
                f"https://{website}/certificates/{cert_id}",
                f"https://{website}/student/certificate/{cert_id}",
                f"https://{website}/verify/{cert_id}",
                f"https://{website}/verify-certificate/{cert_id}",
                f"https://{website}/cert/{cert_id}"
            ]
        }

        patterns = domain_patterns.get(website, domain_patterns["default"])
        headers = {"User-Agent": "Mozilla/5.0"}

        for url in patterns:
            try:
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    if "certificate" in soup.text.lower():
                        webbrowser.open(url)
                        return f"✅ Valid certificate found at: {url}"
            except Exception:
                continue

        return f"❌ No valid verification URL found for {website} with ID {cert_id}"
