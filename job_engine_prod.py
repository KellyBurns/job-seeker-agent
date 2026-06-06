import os
import requests
from flask import Flask
from huggingface_hub import InferenceClient

app = Flask(__name__)

# ==========================================
# 1. SETTINGS & KEYWORD STACK
# ==========================================
CRAWLBASE_TOKEN = os.getenv("CRAWLBASE_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct", token=HF_TOKEN)

# Your precision keyword stack
HEALTHCARE_AI_QUERY = (
    '%22Product+Manager%22+AND+%28LLM+OR+GenAI+OR+%22Agentic+AI%22+OR+%22Hugging+Face%22+'
    'OR+%22AI+development%22+OR+Model+OR+STT+OR+RAG+OR+Python+OR+Flask+OR+GitHub+'
    'OR+Jira+OR+Confluence+OR+%22Digital+Transformation%22+OR+EPIC+OR+HIPAA+'
    'OR+%22Call+Center%22+OR+Agile%29'
)

# Portals with restored keywords and validated f-string formatting
PORTALS = [
    {"company": "Optum / UHG", "url": f"https://careers.unitedhealthgroup.com/search-jobs?acm=ALL&alrpm=ALL&ascf=[%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Linked+to+Site%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Multi+State%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Specific+state+(Contractually+Required)%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+(Nationwide)%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote%22%7D]"},
    {"company": "CVS Health", "url": f"https://jobs.cvshealth.com/us/en/search-results?keywords={HEALTHCARE_AI_QUERY}&p=Aetna&cfWorkLocation=Remote"},
    {"company": "Amgen", "url": f"https://careers.amgen.com/en/search-jobs?acm=ALL&alrpm=ALL&ascf=[%7B%22key%22:%22custom_fields.CareerOpportunities%22,%22value%22:%22Digital+Innovation+and+Technology%22%7D]&k=Product"},
    {"company": "Elevance Health", "url": f"https://careers.elevancehealth.com/jobs?keyword={HEALTHCARE_AI_QUERY}&location=Remote&page_number=1"},
    {"company": "Humana", "url": f"https://careers.humana.com/us/en/c/technology-and-digital-analytics-jobs?keywords={HEALTHCARE_AI_QUERY}"},
    {"company": "Cigna", "url": f"https://jobs.thecignagroup.com/us/en/search-results?keywords={HEALTHCARE_AI_QUERY}&from=0&num=20&gclocation=United%20States&cfWorkLocation=Remote"},
    {"company": "Blue Cross Blue Shield", "url": f"https://www.bcbs.com/careers"},
    {"company": "Mayo Clinic", "url": f"https://jobs.mayoclinic.org/search-jobs/Remote/33647/2/1000000000100/0/0/50/2"}
]

# ==========================================
# 2. ENGINE (Scraping & AI)
# ==========================================
def scrape_with_crawlbase(url):
    if not CRAWLBASE_TOKEN: return ""
    proxies = {
        "http": f"http://{CRAWLBASE_TOKEN}@smartproxy.crawlbase.com:8012",
        "https": f"http://{CRAWLBASE_TOKEN}@smartproxy.crawlbase.com:8012"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=30, verify=False)
        return response.text if response.status_code == 200 else ""
    except: return ""

def analyze_page_with_ai(web_text):
    if not web_text or len(web_text.strip()) < 500: return None
    prompt = f"Analyze the text and extract up to 2 active relevant job listings. Format as HTML blocks. Raw Content: {web_text[:12000]}"
    try:
        return client.text_generation(prompt, max_new_tokens=1500, temperature=0.1)
    except: return None

# ==========================================
# 3. DASHBOARD
# ==========================================
@app.route("/")
def dashboard_home():
    html_body = ""
    for item in PORTALS:
        raw_text = scrape_with_crawlbase(item["url"])
        ai_res = analyze_page_with_ai(raw_text)
        
        if ai_res and "No matching" not in ai_res:
            html_body += ai_res
        else:
            html_body += f"""
<div style="margin: 20px 0; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f7fafc;">
  <strong>{item['company']}</strong><br>
  <a href="{item['url']}" target="_blank" style="color:#0288d1; font-weight:bold;">Launch Direct Search Gateway &rarr;</a>
</div>"""
    return f"<html><body><div style='max-width:800px; margin:auto; font-family:sans-serif;'><h1>Active Job Leads</h1>{html_body}</div></body></html>"

# ==========================================
# 4. RUNTIME (Fixed Port Binding)
# ==========================================
if __name__ == "__main__":
    assigned_port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=assigned_port)
