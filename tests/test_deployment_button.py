#!/usr/bin/env python3
"""
Quick test script to verify deployment button setup
"""

import os
from dotenv import load_dotenv

print("="*60)
print("  Deployment Button - Configuration Test")
print("="*60)
print()

# Load environment variables
load_dotenv()

# Check 1: NETLIFY_TOKEN
print("1. Checking NETLIFY_TOKEN...")
netlify_token = os.getenv('NETLIFY_TOKEN')
if netlify_token:
    print(f"   ✅ NETLIFY_TOKEN found: {netlify_token[:10]}...")
else:
    print("   ❌ NETLIFY_TOKEN not found!")
    print("   → Add to .env file: NETLIFY_TOKEN=your_token_here")
print()

# Check 2: Deployment server
print("2. Checking deployment server...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5001))
if result == 0:
    print("   ✅ Deployment server is running on port 5001")
else:
    print("   ❌ Deployment server is NOT running")
    print("   → Start it with: python deploy_server.py")
sock.close()
print()

# Check 3: Portfolio files
print("3. Checking for portfolio files...")
if os.path.exists('generated_portfolios'):
    files = [f for f in os.listdir('generated_portfolios') if f.endswith('.zip')]
    if files:
        print(f"   ✅ Found {len(files)} portfolio ZIP files")
        print(f"   → Most recent: {files[-1]}")
    else:
        print("   ⚠️  No portfolio ZIP files found")
        print("   → Generate a portfolio first")
else:
    print("   ⚠️  generated_portfolios folder not found")
print()

# Check 4: Required packages
print("4. Checking required packages...")
try:
    import flask
    print("   ✅ Flask installed")
except ImportError:
    print("   ❌ Flask not installed")
    print("   → Install with: pip install flask")

try:
    import requests
    print("   ✅ Requests installed")
except ImportError:
    print("   ❌ Requests not installed")
    print("   → Install with: pip install requests")
print()

# Summary
print("="*60)
print("  Summary")
print("="*60)

all_good = True

if not netlify_token:
    print("❌ Configure NETLIFY_TOKEN in .env")
    all_good = False

if result != 0:
    print("❌ Start deployment server: python deploy_server.py")
    all_good = False

if all_good:
    print("✅ Everything is configured correctly!")
    print()
    print("Next steps:")
    print("1. Generate a portfolio in Streamlit")
    print("2. Click 'Host Portfolio Online'")
    print("3. Purple box should appear")
    print("4. Click 'Open Deployment Page →'")
else:
    print()
    print("⚠️  Please fix the issues above and try again")

print("="*60)
