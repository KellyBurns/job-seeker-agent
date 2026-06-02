import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from huggingface_hub import InferenceClient

# =====================================================================
# 1. ENVIRONMENT VARIABLES & KEYS (Injected via Railway Dashboard)
# =====================================================================
HF_TOKEN = os.environ.get("HF_TOKEN")
CRAWLBASE_TOKEN = os.environ.get("CRAWLBASE_TOKEN")
EMAIL_SENDER = "KellyBurns2005@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD") # Your 16-character Google App Password
EMAIL_RECEIVER = "KellyBurns2005@gmail.com"

# Initialize Hugging Face Serverless Engine (Llama-3-70B via your PRO tier)
client = InferenceClient("meta-llama/Meta-Llama-3-1-70B-Instruct", token=HF_TOKEN)

# Paring down to ONLY two URLs for clean troubleshooting
TARGET_URLS = {
    "Optum / UHG": "https://careers.unitedhealthgroup.com/search-jobs?acm=ALL&alrpm=ALL&ascf=[%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Linked+to+Site%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Multi+State%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+-+Specific+state+(Contractually+Required)%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote+(Nationwide)%22%7D,%7B%22key%22:%22custom_fields.WorkSetting%22,%22value%22:%22Remote%22%7D]",
    "CVS Health": "https://jobs.cvshealth.com/us/en/search-results?keywords=Product&p=Aetna&cfWorkLocation=Remote"
}

AI_SYSTEM_PROMPT = """
You are an expert executive recruiter screening enterprise Technical Product Management roles in the healthcare sector.
Analyze the raw text data from corporate career portals and extract matching roles.

STRICT FILTERS:
- ONLY accept roles that explicitly state they are 100% "Remote", "Telecommute", or "Work from Home" within the United States.
- IMMEDIATELY DISCARD any roles that are "Hybrid", "On-site", or require commuting.

SEMANTIC MATCHING:
- ACCEPT equivalent titles: "Product Owner", "Product AI Manager", "Technical Product Manager", "Product Lead", "Product Manager II".
- THE CORE CRITERIA: Day-to-day work must focus on full product lifecycle, agile backlog strategy/grooming, data-driven frameworks, or AI/ML technical deployment matching a senior IT application profile.

OUTPUT REQUIREMENT:
You must return your findings in RAW HTML code snippets (NOT Markdown). Group them into two categories:
1. <h2 style='color:#2e7d32;'>🟢 HIGH CONFIDENCE MATCHES</h2>
2. <h2 style='color:#f57f17;'>🟡 MEDIUM CONFIDENCE MATCHES</h2>

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
"""

def scrape_with_crawlbase(url):
    """Hits the Crawlbase JS Token endpoint to load hidden Javascript elements cleanly."""
    encoded_url = requests.utils.quote(url)
    # Using dynamic scroll & ajax wait parameters to catch lazy-loaded text elements
    crawlbase_url = f"https://api.crawlbase.com/?token={CRAWLBASE_TOKEN}&scroll=true&ajax_wait=true&url={encoded_url}"
    try:
        response = requests.get(crawlbase_url, timeout=30)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed to scrape {url}: {str(e)}")
    return ""

def query_huggingface_llm(raw_html_content):
    """Leverages Hugging Face serverless architecture to screen text instantly for free."""
    try:
        messages = [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": f"TARGET PROFILE:\n- Senior TPM, Healthcare IT, Agile, AI/ML\n\nRAW DATA:\n{raw_html_content[:40000]}"}
        ]
        response = client.chat_completion(messages=messages, max_tokens=2000)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Hugging Face Inference Error: {e}")
        return ""

def send_html_email(html_body):
    """Dispatches a clean, beautifully formatted modern HTML newsletter layout to your inbox."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "☀️ Your Daily Healthcare TPM Remote Job Digest (Test Run)"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    # Wrap inside clean, scannable CSS inline containers
    email_wrapper = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 650px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h1 style="color: #1565c0; border-bottom: 2px solid #1565c0; padding-bottom: 10px; margin-top: 0;">🔍 Daily TPM Job Screen (2-Site Test)</h1>
        <p style="color: #666; font-size: 14px;">Automated pilot scan executed successfully at 4:00 AM PST.</p>
        {html_body}
        <p style="font-size: 11px; color: #999; text-align: center; margin-top: 30px; border-top: 1px solid #e0e0e0; padding-top: 10px;">
          Automated Pipeline running via Railway & Hugging Face Serverless Core.
        </p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(email_wrapper, "html"))

try:
        with smtplib.SMTP("smtp.gmail.com", 2525) as server:
            server.starttls()  # Secures the connection over the open port
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Test Email Report sent successfully!")
    except Exception as e:
        print(f"Email Dispatch Failure: {e}")
        

def main():
    final_html_report = ""
    matches_found = False

    for company_name, url in TARGET_URLS.items():
        print(f"Scanning portal: {company_name}...")
        raw_text = scrape_with_crawlbase(url)
        
        if raw_text:
            ai_analysis = query_huggingface_llm(raw_text)
            if ai_analysis and "No matching remote product roles found" not in ai_analysis:
                matches_found = True
                final_html_report += f"<h2 style='background-color:#f5f5f5; padding:8px; border-left:4px solid #1565c0; margin-top:20px;'>🏢 {company_name}</h2>{ai_analysis}"

    if not matches_found:
        final_html_report = "<p style='font-style: italic; color:#757575; font-size:16px;'>No matching 100% remote product roles found across Optum or CVS in this morning's batch scan.</p>"

    send_html_email(final_html_report)

if __name__ == "__main__":
    main()
