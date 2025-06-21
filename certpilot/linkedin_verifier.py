import google.generativeai as genai
from serpapi import GoogleSearch

# === CONFIGURE YOUR API KEYS ===
GEMINI_API_KEY = "# Replace with your Gemini API key"  # Replace with your Gemini API key
SERPAPI_KEY = "# Replace with your SerpAPI key"  # Replace with your SerpAPI key

# === SETUP GEMINI ===
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# === FETCH POSTS USING SERPAPI ===
def get_linkedin_posts_fast(company_name, serpapi_key):
    search = GoogleSearch({
        "q": f'site:linkedin.com/posts "{company_name}"',
        "api_key": serpapi_key,
        "num": 5
    })
    results = search.get_dict()
    return [res["snippet"] for res in results.get("organic_results", []) if "linkedin.com/posts" in res.get("link", "")]

# === GEMINI CONTENT VERIFIER ===
def check_fake_or_real(post_text):
    prompt = f"""
You are an AI assistant verifying if a LinkedIn post spreads fake or misleading claims about a company.

POST TEXT:
{post_text}

Give the conclusion only in this format:
{{
  "status": "Good" or "Fake",
  "reason": "short explanation"
}}
"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# === EXPORTABLE FUNCTION ===
def verify_linkedin_posts(company):
    print(f"\n🔎 Searching LinkedIn posts mentioning: {company}\n")
    post_snippets = get_linkedin_posts_fast(company, SERPAPI_KEY)

    results = []
    if not post_snippets:
        return [{"status": "❌ No LinkedIn posts found", "post": None}]

    for i, post in enumerate(post_snippets, 1):
        print(f"\n📄 Post #{i}:\n{post}\n")
        analysis = check_fake_or_real(post)
        print(f"🤖 Gemini Analysis:\n{analysis}\n")
        results.append({
            "post": post,
            "analysis": analysis
        })

    return results
