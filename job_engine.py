import os
import requests
from flask import Flask
from huggingface_hub import InferenceClient

app = Flask(__name__)

# ==========================================
# 1. ENVIRONMENT SETTINGS
# ==========================================
CRAWLBASE_TOKEN = os.getenv("CRAWLBASE_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize the Hugging Face AI client
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

# Your specific target search configurations
PORTALS = [
    {
        "company": "Optum",
        "search_title": "Technical Product Manager - Remote",
        "direct_query_url": "https://careers.unitedhealthgroup.com/search-jobs?q=Product+Manager&gl=US",
        "why_fits": "Aligns with your extensive IT application background and deep domain experience in enterprise healthcare systems."
    },
    {
        "company": "CVS Health",
        "search_title": "Senior IT Application Engineer / Product Owner",
        "direct_query_url": "https://jobs.cvshealth.com/search-jobs?q=Product+Manager",
        "why_fits": "Directly matches your 19 years of healthcare tech sector expertise and Scrum product ownership certifications."
    }
]

# ==========================================
# 2. CONNECTIVITY & AI ENGINE
# ==========================================
def scrape_with_crawlbase(url):
    """Hits the Crawlbase JS Token endpoint to load hidden elements cleanly."""
    if not CRAWLBASE_TOKEN:
        return ""
    encoded_url = requests.utils.quote(url)
    crawlbase_url = f"https://api.crawlbase.com/?token={CRAWLBASE_TOKEN}&scroll=true&ajax_wait=true&url={encoded_url}"
    try:
        response = requests.get(crawlbase_url, timeout=30)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Scrape timeout/error: {str(e)}")
    return ""

def analyze_page_with_ai(web_text, target_role):
    """Sends raw content to Hugging Face to extract live deep links."""
    if not web_text or len(web_text.strip()) < 500: # If the page source is empty or too short
        return None
        
    prompt = f"""
Analyze the raw text content from this corporate careers page and extract any active job listings matching: {target_role}.

For each matching job found, construct a clean block exactly like this:
<p style="margin-bottom:15px;">
  <strong>Job Title:</strong> [Exact Title]<br>
  <strong>Company:</strong> [Company Name]<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Direct Link:</strong> <a href="[Insert the specific extracted job URL]" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to View & Apply</a><br>
  <strong>Why It Fits:</strong> [1-2 sentences detailing semantic alignment]<br>
</p>
<hr style='border: 0; border-top: 1px solid #eee;'>

If no roles match from the text, reply strictly with: "No matching remote product roles found."

Raw Web Content:
{web_text[:12000]}
"""
    try:
        output = client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)
        if "No matching remote product roles found." in output or len(output.strip()) < 20:
            return None
        return output
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return None

# ==========================================
# 3. THE FLASK ROUTE (Your Live Dashboard)
# ==========================================
@app.route("/")
def dashboard_home():
    html_body_content = ""
    
    for item in PORTALS:
        print(f"Scanning {item['company']} live portal...")
        raw_html_text = scrape_with_crawlbase(item["direct_query_url"])
        
        # Try to extract the live deep link via AI
        ai_extraction = analyze_page_with_ai(raw_html_text, item["search_title"])
        
        if ai_extraction:
            # If the AI successfully read the data and found a deep link, use it!
            html_body_content += ai_extraction
        else:
            # FALLBACK: If the portal blocked the scraper, output your target title with a direct portal query link
            html_body_content += f"""
<p style="margin-bottom:15px; background-color: #fffaf0; padding: 15px; border-radius: 6px; border: 1px solid #feebc8;">
  <strong style="color: #dd6b20; font-size: 0.85rem; uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 5px;">⚠️ Live Scraping Blocked - Target Portal Query Ready</strong>
  <strong>Job Title Target:</strong> {item['search_title']}<br>
  <strong>Company:</strong> {item['company']}<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Direct Link:</strong> <a href="{item['direct_query_url']}" target="_blank" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to Run Live Search on Portal</a><br>
  <strong>Why It Fits:</strong> {item['why_fits']}<br>
</p>
<hr style='border: 0; border-top: 1px solid #eee;'>
            """

    # Master layout wrapper
    master_layout = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily Job Leads Dashboard</title>
        <meta name="robots" content="noindex, nofollow">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: #f7fafc; 
                color: #2d3748; 
            }}
            .wrapper {{ max-width: 750px; margin: 30px auto; padding: 25px; background: #ffffff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            h1 {{ color: #1a202c; border-bottom: 3px solid #e2e8f0; padding-bottom: 14px; font-size: 1.65rem; margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <h1>Latest Remote Job Matches</h1>
            {html_body_content}
        </div>
    </body>
    </html>
    """
    return master_layout

# ==========================================
# 4. START THE WEB RUNTIME
# ==========================================
if __name__ == "__main__":
    assigned_port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=assigned_port)
