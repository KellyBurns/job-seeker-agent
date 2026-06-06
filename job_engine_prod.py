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

# Helper to append keywords to base URLs
def build_url(base_url, query_param="q="):
    return f"{base_url}&{query_param}{HEALTHCARE_AI_QUERY}"

# Portals with restored keywords
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
# 2. ENGINE & DASHBOARD (Unchanged)
# ==========================================
# [All previous scrape_with_crawlbase, analyze_page_with_ai, and dashboard_home logic remains the same]
