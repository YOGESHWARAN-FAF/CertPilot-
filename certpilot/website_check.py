import requests
import whois
from datetime import datetime
from threading import Thread

class WebsiteVerifier(Thread):
    @staticmethod
    def verify(url):
        results = []

        # Ensure URL starts with https://
        if not url.startswith("http"):
            url = "https://" + url
        elif url.startswith("http://"):
            url = url.replace("http://", "https://")

        domain = url.replace("https://", "").split("/")[0]

        # HTTPS & status check
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results.append("✅ HTTPS supported and website is reachable (200 OK).")
            else:
                results.append(f"⚠️ HTTPS supported but returned status code: {response.status_code}")
        except Exception as e:
            results.append(f"❌ HTTPS request failed: {str(e)}")

        # Domain age check
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            age_days = (datetime.now() - creation_date).days
            results.append(f"🕒 Domain age: {int(age_days / 365)} years (Created on {creation_date.date()})")
        except Exception as e:
            results.append(f"❌ Failed to fetch domain info: {str(e)}")

        return "\n".join(results)
