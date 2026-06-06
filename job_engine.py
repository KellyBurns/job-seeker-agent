import os
import time
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

print("Container initialized. Preparing scraping pipeline...")

# ==========================================
# 1. THE SCRAPER (Where your data goes)
# ==========================================
# This mock data represents what your Crawlbase loop extracts.
# It populates your specific, target career leads cleanly.
jobs_found = [
    {"title": "Technical Product Manager - Remote", "company": "Optum", "url": "https://careers.unitedhealthgroup.com/"},
    {"title": "Senior IT Application Engineer", "company": "CVS Health", "url": "https://jobs.cvshealth.com/"}
]

# ==========================================
# 2. GENERATE THE HTML SCOREBOARD
# ==========================================
html_content = """
<html>
<head>
    <title>Daily Job Leads</title>
    <meta name="robots" content="noindex, nofollow">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        h1 { color: #333; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
        ul { list-style-type: none; padding: 0; }
        li { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        a { color: #0066cc; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .meta { color: #666; font-size: 0.9em; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>Latest Remote Job Matches</h1>
    <ul>
"""

for job in jobs_found:
    html_content += f"""
        <li>
            <strong>{job['company']}</strong>: 
            <a href="{job['url']}" target="_blank">{job['title']}</a>
            <div class="meta">Status: Confirmed Remote</div>
        </li>
    """

html_content += """
    </ul>
</body>
</html>
"""

# Write the static file cleanly to the root directory
with open("index.html", "w") as f:
    f.write(html_content)

print("HTML interface compiled successfully.")

# ==========================================
# 3. THE LIGHTWEIGHT WEB SERVER
# ==========================================
def run_web_server():
    # Railway automatically passes an open network port using the PORT environment variable
    port = int(os.getenv("PORT", 8080))
    server_address = ("", port)
    
    # SimpleHTTPRequestHandler automatically reads 'index.html' and hosts it to the web
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Web server smoothly broadcasting on port {port}...")
    httpd.serve_forever()

# Launch the server so it keeps the container alive and active for you
run_web_server()
