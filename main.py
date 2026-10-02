import scratchattach as sa
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import threading
import os

app = FastAPI()

# Credentials and project info from environment variables on Render
SCRATCH_USER = os.getenv("SCRATCH_USER")
SCRATCH_PASSWORD = os.getenv("SCRATCH_PASSWORD")
PROJECT_ID = os.getenv("PROJECT_ID")

# Initialize Scratch session and Cloud Requests
try:
    session = sa.login(SCRATCH_USER, SCRATCH_PASSWORD)
    conn = session.connect_cloud(project_id=PROJECT_ID)
    client = sa.CloudRequests(conn)
    
    @client.request
    def get_page(url):
        """Called when Scratch sends a URL request"""
        if not url.startswith("http"):
            url = "https://" + url
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text content and limit characters for Scratch limits
            text_content = soup.get_text()[:200] 
            return text_content
        except Exception as e:
            return f"Error loading URL: {str(e)}"

    def run_scratch_listener():
        client.run()

    # Run the scratch listener in a background thread so FastAPI can run on Render's port
    threading.Thread(target=run_scratch_listener, daemon=True).start()

except Exception as e:
    print(f"Scratch connection failed: {e}")

@app.get("/")
def read_root():
    return {"status": "Scratch browser bridge is running!"}
