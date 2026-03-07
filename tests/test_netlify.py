"""
Quick Netlify API test - run: python test_netlify.py
"""
import os, io, zipfile, requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NETLIFY_TOKEN")

print("=== Netlify Deployment Test ===")
print(f"Token found: {bool(token)}")
if token:
    print(f"Token starts with: {token[:20]}...")

# Step 1: Verify token
print("\n--- Step 1: Verify token ---")
r = requests.get(
    "https://api.netlify.com/api/v1/user",
    headers={"Authorization": f"Bearer {token}"},
    timeout=15
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    print(f"Logged in as: {d.get('email', d.get('full_name', 'unknown'))}")
else:
    print(f"ERROR: {r.text[:300]}")
    exit(1)

# Step 2: Create a test site
print("\n--- Step 2: Create site ---")
site_resp = requests.post(
    "https://api.netlify.com/api/v1/sites",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={},
    timeout=30
)
print(f"Status: {site_resp.status_code}")
if site_resp.status_code not in (200, 201):
    print(f"ERROR: {site_resp.text[:300]}")
    exit(1)

site_data = site_resp.json()
site_id = site_data.get("id")
site_url = site_data.get("ssl_url") or site_data.get("url") or ""
print(f"Site ID: {site_id}")
print(f"Site URL: {site_url}")

# Step 3: Upload a minimal test ZIP
print("\n--- Step 3: Upload test deploy ---")
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("index.html", "<h1>Test Portfolio - it works!</h1>")
buf.seek(0)

deploy_resp = requests.post(
    f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/zip"},
    data=buf.read(),
    timeout=120
)
print(f"Status: {deploy_resp.status_code}")
if deploy_resp.status_code not in (200, 201):
    print(f"ERROR: {deploy_resp.text[:300]}")
    exit(1)

deploy_data = deploy_resp.json()
print(f"Deploy state: {deploy_data.get('state')}")

live_url = (
    deploy_data.get("ssl_url")
    or deploy_data.get("url")
    or site_data.get("ssl_url")
    or site_data.get("url")
    or f"https://{site_data.get('name', '')}.netlify.app"
)
print(f"\n✅ SUCCESS! Live URL: {live_url}")
print(f"Admin URL: {site_data.get('admin_url', 'N/A')}")
