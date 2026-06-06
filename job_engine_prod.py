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

# HEALTHCARE, TRANSFORMATION, AI ENGINE & ENTERPRISE TOOL STACK QUERY
HEALTHCARE_AI_QUERY = (
    '%22Product+Manager%22+AND+%28LLM+OR+GenAI+OR+%22Agentic+AI%22+OR+%22Hugging+Face%22+'
    'OR+%22AI+development%22+OR+Model+OR+STT+OR+RAG+OR+Python+OR+Flask+OR+GitHub+'
    'OR+Jira+OR+Confluence+OR+%22Digital+Transformation%22+OR+EPIC+OR+HIPAA+'
    'OR+%22Call+Center%22+OR+Agile%29'
)

OPTUM_COMBINED_URL = f"https://careers.unitedhealthgroup.com/search-jobs?q={HEALTHCARE_AI_QUERY}&gl=US"
CVS_COMBINED_URL = "https://jobs.cvshealth.com/us/en"

PORTALS = [
    {
        "company": "Optum",
        "search_title": "Technical Product Manager - Healthcare AI & Operations (1-6 Years PM Exp Target)",
        "direct_query_url": OPTUM_COMBINED_URL,
        "why_fits": "Directly matches your specialized domain expertise managing Epic EHR integrations, ensuring strict HIPAA/PHI data compliance frameworks, and optimization modeling for high-volume healthcare call center networks."
    },
    {
        "company": "CVS Health",
        "search_title": "Technical Product Manager - Healthcare AI & Operations (1-6 Years PM Exp Target)",
        "direct_query_url": CVS_COMBINED_URL,
        "why_fits": "Directly leverages your unique sweet spot: driving 0-1 delivery pipelines for conversational AI platforms, orchestrating speech-to-text systems inside contact centers, and managing clinical system transformations safely within regulatory boundaries."
    }
]

# ==========================================
# 2. CONNECTIVITY & AI ENGINE 
# ==========================================
def scrape_with_crawlbase(url):
    """
    Routes traffic through the Crawlbase Smart Proxy network using real desktop 
    user-agents to bypass strict corporate anti-bot security walls.
    """
    if not CRAWLBASE_TOKEN:
        return ""
        
    proxies = {
        "http": f"http://{CRAWLBASE_TOKEN}@smartproxy.crawlbase.com:8012",
        "https://http://{CRAWLBASE_TOKEN}@smartproxy.crawlbase.com:8012"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Smart Proxy tunnel timeout/error: {str(e)}")
    return ""

def analyze_page_with_ai(web_text, target_role):
    """
    Sends raw content to Hugging Face to isolate exactly 2 distinct matching jobs per company,
    filtering within a 1-6 year product experience framework.
    """
    if not web_text or len(web_text.strip()) < 500:
        return None
        
    prompt = f"""
Analyze the raw text content from this corporate careers page and extract exactly 2 distinct active job listings matching: {target_role}.
Filter strictly for positions targeting 1 to 6 years of experience in Product Management (e.g., jobs asking for 2+ years, 3+ years, 5 years, or up to 6 years of experience) to avoid bloated senior director tracks. Do not stop at just 1 listing—extract exactly 2 distinct positions if they are present in the text.

Evaluate semantic alignment by comparing requirements against the candidate's core Technical Product Manager (TPM) profile:
- Enterprise Collaboration & Tooling: Daily proficiency orchestrating backlogs inside Jira, documenting system technical taxonomies in Confluence, and aligning cross-functional execution paths via GitHub.
- Hands-on AI Model & Lifecycle Management: Direct experience working with the Hugging Face ecosystem, managing Inference Clients, orchestrating raw AI development endpoints, and evaluating open-source model architectures (like Llama) against business requirements.
- Technical Execution & Prototyping: Strong ability to audit/debug raw Python source code, build Python/Flask application wrappers, navigate version control pipelines, and deploy live containerized applications via modern CI/CD architectures (Railway).
- Domain Context (Kaiser Permanente & Corporate Scale): Owned product taxonomy and technical roadmaps for "CHATS" enterprise cloud AI platform; managed 1M+ monthly call operational scaling metrics using STT, RAG, and NLP workflows. Led 40+ complex API integrations (including Epic EHR) under 100% strict HIPAA/PHI compliance frameworks. 
- Agile & Education Foundations: Transitioned a 60+ member organization via the Agile Product Maturity Model (PMM) and PI Planning. Academic backing in Agentic AI Foundations (Harvard 2026) and AI Product Design (MIT 2024).

For each matching job found (exactly 2), construct a clean block exactly like this:
<p style="margin-bottom:15px;">
  <strong>Job Title:</strong> [Exact Title]<br>
  <strong>Company:</strong> [Company Name]<br>
  <strong>Location:</strong> Remote - US<br>
  <strong>Experience Range:</strong> 1-6 Years Product Management Experience<br>
  <strong>Direct Link:</strong> <a href="[Insert the specific extracted job URL]" style="color:#0288d1; font-weight:bold; text-decoration:underline;">Click Here to View & Apply</a><br>
  <strong>Why It Fits:</strong> [Detail precise structural alignment using their hands-on ability to interface with Hugging Face models, debug Python source code, manage delivery pipelines using Jira/Confluence/GitHub, or coordinate enterprise agile frameworks in 1-2 powerful sentences]<br>
</p>
<hr style='border: 0; border-top: 1px solid #eee;'>

If no roles match from the text, reply strictly with: "No matching remote product roles found."

Raw Web Content:
{web_text[:12000]}
"""
    try:
        output = client.text_generation(prompt, max_new_tokens=1500, temperature=0.1)
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
            # FALLBACK TEMPLATE
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
