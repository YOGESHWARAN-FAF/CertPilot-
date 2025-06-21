import google.generativeai as genai
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from threading import Thread

class ReviewScraperPlaywright():
    REVIEW_KEYWORDS = ["review", "feedback", "testimonial", "comment", "opinion", "student", "learner", "people"]
  
    @staticmethod
    def find_reviews_in_html(soup):
        reviews = []
        all_divs = soup.find_all("div")
        for div in all_divs:
            class_str = " ".join(div.get("class", []))
            text = div.get_text(strip=True)
            if any(k in class_str.lower() for k in ReviewScraperPlaywright.REVIEW_KEYWORDS) or \
               any(k in text.lower() for k in ReviewScraperPlaywright.REVIEW_KEYWORDS):
                if len(text) > 10:
                    reviews.append(text)
        return reviews

    @staticmethod
    def scrape_reviews(url):
        if not url.startswith("http"):
            url = "https://" + url

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                print(f"🌐 Opening: {url}")
                page.goto(url, timeout=30000)
                page.wait_for_timeout(3000)
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                reviews = ReviewScraperPlaywright.find_reviews_in_html(soup)
                if reviews:
                    browser.close()
                    return reviews

                print("🔄 No reviews found. Searching sub-pages...")
                links = soup.find_all("a", href=True)
                visited = set()
                for link in links:
                    href = link["href"]
                    if not href.startswith("http"):
                        href = page.url.rstrip("/") + "/" + href.lstrip("/")
                    if href not in visited:
                        visited.add(href)
                        try:
                            page.goto(href, timeout=10000)
                            page.wait_for_timeout(2000)
                            sub_html = page.content()
                            sub_soup = BeautifulSoup(sub_html, "html.parser")
                            reviews = ReviewScraperPlaywright.find_reviews_in_html(sub_soup)
                            if reviews:
                                browser.close()
                                return reviews
                        except:
                            continue
                browser.close()
                return []
            except Exception as e:
                browser.close()
                print(f"❌ Review scraping error: {e}")
                return []

class GeminiReviewAnalyzer:
    @staticmethod
    def summarize_and_rate_reviews(reviews, api_key):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        joined_reviews = "\n\n".join(reviews[:10])  # Limit to 10 reviews
        prompt = f"""
You are an AI assistant. Analyze the following certificate reviews and return:

- A short summary of the overall feedback.
- Sentiment (Positive, Neutral, Negative).
- A star rating (1 to 5 stars).

Return the output in this exact JSON format:
{{
  "Summary": "...",
  "Sentiment": "...",
  "Star Rating": "x/5"
}}

REVIEWS:
{joined_reviews}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
