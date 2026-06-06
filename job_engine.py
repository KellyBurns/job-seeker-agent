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

# Initialize the Hugging Face AI client using a fast, powerful open-source model
# (Using Meta's Llama-3-8B-Instruct via the serverless API)
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

# ==========================================
# 2. CONNECTIVITY & AI ENGINE
# ==========================================
def scrape_with_crawlbase(url):
    """Hits the Crawlbase JS Token endpoint to load hidden Javascript elements cleanly."""
    if not CRAWLBASE_TOKEN:
        print("Error: Missing CRAWLBASE_TOKEN in environment variables.")
        return ""
        
    encoded_url = requests.utils.quote(url)
    crawlbase_url = f"https://api.crawlbase.com/?token={CRAWLBASE_TOKEN}&scroll=true&ajax_wait=true&url={encoded_url}"
    try:
        response = requests.get(crawlbase_url, timeout=30)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed to scrape {url}: {str(e)}")
    return ""

def analyze_page_with_ai(web_text):
    """Sends the raw web content to the Hugging Face LLM to extract target roles."""
    if not web_text:
        return "No matching remote product roles found."
        
    prompt = f"""
You are an expert IT job searching assistant. Analyze the raw text content from this corporate careers page and extract any active job listings that match remote Product Manager, Technical Product Manager, or IT Application Engineering positions.

For each job found, construct a clean block exactly like this:
<p style="margin-bottom:15px;">
  <strong>Job Title:</strong> [Exact Title]<br>
  <strong>Company:</strong> [Company Name]<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Direct Link:</strong> <a href="[Insert the specific extracted job URL or portal link]" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to View & Apply</a><br>
  <strong>Why It Fits:</strong> [1-2 sentences detailing semantic alignment]<br>
</p>
<hr style='border: 0; border-top: 1px solid #eee;'>

If no roles match from the text, reply strictly with: "No matching remote product roles found."

Raw Web Content:
{web_text[:15000]}  # Keep within context boundaries
"""
    try:
        # Generate text using the serverless Hugging Face API
        output = client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)
        return output
    except Exception as e:
        print(f"Hugging Face Inference Error: {e}")
        return f"<p>Error analyzing data with AI: {str(e)}</p>"

# ==========================================
# 3. THE FLASK ROUTE (Your Live Dashboard)
# ==========================================
@app.route("/")
def dashboard_home():
    # Define the precise job URLs you want scanned
    portals = [
        "https://careers.unitedhealthgroup.com/search-jobs?q=Product+Manager&gl=US", # Optum parent portal query
        "https://jobs.cvshealth.com/search-jobs?q=Product+Manager"
    ]
    
    html_body_content = ""
    
    for url in portals:
        print(f"Scanning target portal: {url}")
        raw_html_text = scrape_with_crawlbase(url)
        
        # Feed the text to your Hugging Face model
        ai_extraction = analyze_page_with_ai(raw_html_text)
        
        # If it found matching entries, add them to our layout page
        if "No matching remote product roles found." not in ai_extraction:
            html_body_content += ai_extraction

    # If the combined loops found absolutely nothing across all pages
    if not html_body_content.strip():
        html_body_content = "<p style='color: #718096; font-style: italic;'>No matching remote product roles found today.</p>"

    # Master dashboard UI template container
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
    print(f"Launching AI Web interface on port {assigned_port}...")
    app.run(host="0.0.0.0", port=assigned_port)
