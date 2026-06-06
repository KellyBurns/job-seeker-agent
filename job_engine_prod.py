import os
import requests
from flask import Flask
from huggingface_hub import InferenceClient

app = Flask(__name__)

# ==========================================
# 1. ENVIRONMENT SETTINGS & PREFERENCES
# ==========================================
CRAWLBASE_TOKEN = os.getenv("CRAWLBASE_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize the Hugging Face AI client
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

# Premium configurations targeting the highly lucrative 1-6 years PM experience bracket
PORTALS = [
    {
        "company": "Optum",
        "search_title": "Technical Product Manager - Enterprise AI Platforms (1-6 Years PM Exp Target)",
        # Custom-encoded query string targeting core Product Manager tags alongside high-paying AI infrastructure keywords
        "direct_query_url": "https://careers.unitedhealthgroup.com/search-jobs?q=%22Product+Manager%22+AND+%28LLM+OR+GenAI+OR+%22Digital+Transformation%22%29&gl=US",
        "why_fits": "Perfect alignment for the 1-6 year experience sweet spot. It leverages your hands-on background deploying RAG-grounded LLMs and managing complex Epic EHR system integrations, letting your technical execution outshine long legacy PM track requirements."
    },
    {
        "company": "CVS Health",
        "search_title": "Product Manager - AI, Analytics & Digital Transformation (1-6 Years PM Exp Target)",
        # Specifically maps to CVS's high-yield modern platform initiatives requiring 3-5 years of agile product ownership
        "direct_query_url": "https://jobs.cvshealth.com/search-jobs?q=%22Product+Manager%22+AND+%28AI+OR+Analytics+OR+Conversational%29",
        "why_fits": "Perfect match for mid-tier experience requirements. It highlights your proven capacity to drive high-velocity 0-1 delivery cycles, manage large-scale interactive systems, and deploy speech-to-text configurations under strict compliance parameters."
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
    """Sends raw content to Hugging Face to isolate jobs strictly within a 1-6 year product experience framework."""
    if not web_text or len(web_text.strip()) < 500:
        return None
        
    prompt = f"""
Analyze the raw text content from this corporate careers page and extract any active job listings matching: {target_role}.
Filter strictly for positions targeting 1 to 6 years of experience in Product Management (e.g., jobs asking for 2+ years, 3+ years, 5 years, or up to 6 years of experience) to avoid bloated senior director/10+ year legacy tracks.

Prioritize high-compensation roles valuing these specific technical attributes: GenAI, RAG-grounded LLMs, Speech-to-Text (STT), 0-1 product creation, Digital Transformation, complex API orchestration, HIPAA compliance, and Agile Change Champion leadership.

For each matching job found, construct a clean block exactly like this:
<p style="margin-bottom:15px;">
  <strong>Job Title:</strong> [Exact Title]<br>
  <strong>Company:</strong> [Company Name]<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Experience Range:</strong> 1-6 Years Product Management Experience<br>
  <strong>Direct Link:</strong> <a href="[Insert the specific extracted job URL]" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to View & Apply</a><br>
  <strong>Why It Fits:</strong> [Detail semantic alignment using their experience in high-impact AI orchestration, 0-1 delivery, or leading cross-functional teams in 1-2 powerful sentences]<br>
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
        print(f"Scanning {item['company']} premium portal queries...")
        raw_html_text = scrape_with_crawlbase(item["direct_query_url"])
        
        ai_extraction = analyze_page_with_ai(raw_html_text, item["search_title"])
        
        if ai_extraction:
            html_body_content += ai_extraction
        else:
            # FALLBACK TEMPLATE: Tailored strictly with your 1-6 year experience profile parameters
            html_body_content += f"""
<p style="margin-bottom:15px; background-color: #fffaf0; padding: 15px; border-radius: 6px; border: 1px solid #feebc8;">
  <strong style="color: #dd6b20; font-size: 0.85rem; uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 5px;">⚠️ Live Scraping Blocked - Target Portal Query Ready</strong>
  <strong>Job Title Target:</strong> {item['search_title']}<br>
  <strong>Company:</strong> {item['company']}<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Experience Range:</strong> 1-6 Years Product Management Experience<br>
  <strong>Direct Link:</strong> <a href="{item['direct_query_url']}" target="_blank" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to Run Live Search on Portal</a><br>
  <strong>Why It Fits:</strong> {item['why_fits']}<br>
</p>
<hr style='border: 0; border-top: 1px solid #eee;'>
            """

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
            h1 {{ color: #1a202c; border-bottom: 3px solid #e2e8f0; padding-bottom: 14px; font-size: 1.65rem;
