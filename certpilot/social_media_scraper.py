from playwright.sync_api import sync_playwright

class SocialMediaScraper:

    @staticmethod
    def ensure_http(url: str) -> str:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            return "https://" + url
        return url

    @staticmethod
    def scrape_social_and_check(website: str) -> dict:
        result = {}
        website = SocialMediaScraper.ensure_http(website)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                print(f"🌐 Visiting: {website}")
                page.goto(website, timeout=10000)

                html = page.content()

                # Extract common social media links from footer or whole page
                links = page.query_selector_all("a")
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    if "linkedin.com" in href:
                        result["LinkedIn"] = href
                    elif "facebook.com" in href:
                        result["Facebook"] = href
                    elif "instagram.com" in href:
                        result["Instagram"] = href
                    elif "twitter.com" in href or "x.com" in href:
                        result["Twitter"] = href
                    elif "youtube.com" in href:
                        result["YouTube"] = href

                browser.close()

                if result:
                    return {"Found Social Links": result}
                else:
                    return {"Note": "No social media links found on website."}

        except Exception as e:
            return {"Error": str(e)}
