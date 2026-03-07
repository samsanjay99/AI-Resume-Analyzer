#!/usr/bin/env python3
"""
Test Netlify Deployment - Verify URL is returned
"""

import os
import sys
import tempfile
import zipfile
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*70)
print("  NETLIFY DEPLOYMENT TEST")
print("="*70)
print()

# Check 1: Token
print("Step 1: Checking NETLIFY_TOKEN...")
token = os.getenv('NETLIFY_TOKEN')
if not token:
    print("   ❌ NETLIFY_TOKEN not found in .env")
    print("   → Add: NETLIFY_TOKEN=your_token_here")
    sys.exit(1)
print(f"   ✅ Token found: {token[:10]}...")
print()

# Check 2: Create test portfolio
print("Step 2: Creating test portfolio...")
test_dir = tempfile.mkdtemp(prefix="test_portfolio_")
test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Portfolio</title>
</head>
<body>
    <h1>Test Portfolio</h1>
    <p>This is a test deployment from Smart Resume AI</p>
</body>
</html>"""

with open(os.path.join(test_dir, 'index.html'), 'w') as f:
    f.write(test_html)

print(f"   ✅ Test portfolio created at: {test_dir}")
print()

# Check 3: Test deployment function
print("Step 3: Testing deploy_to_netlify function...")
print("   (This will actually deploy to Netlify)")
print()

# Import the function from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import deploy_to_netlify
    
    print("   🚀 Starting deployment...")
    result = deploy_to_netlify(test_dir)
    
    print()
    print("="*70)
    print("  DEPLOYMENT RESULT")
    print("="*70)
    print()
    
    if result.get('success'):
        print("✅ SUCCESS!")
        print()
        print(f"Live URL: {result.get('live_url')}")
        print(f"Site ID: {result.get('site_id')}")
        print(f"Admin URL: {result.get('admin_url')}")
        print()
        
        # Verify URL
        live_url = result.get('live_url')
        if live_url:
            print("✅ URL WAS RETURNED!")
            print()
            print(f"You can test it here: {live_url}")
            print()
            
            # Test if URL is accessible
            print("Testing if URL is accessible...")
            import requests
            try:
                response = requests.get(live_url, timeout=10)
                if response.status_code == 200:
                    print("✅ URL is accessible and working!")
                else:
                    print(f"⚠️  URL returned status code: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Could not access URL yet (may take a minute): {e}")
        else:
            print("❌ NO URL RETURNED!")
            print("   This is a problem - deployment succeeded but no URL")
    else:
        print("❌ DEPLOYMENT FAILED")
        print()
        print(f"Error: {result.get('error')}")
        print()
        print("Common issues:")
        print("1. Invalid NETLIFY_TOKEN")
        print("2. Network connection problem")
        print("3. Netlify API issue")
    
    print()
    print("="*70)
    
except ImportError as e:
    print(f"   ❌ Could not import deploy_to_netlify: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Deployment error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

print()
print("="*70)
print("  TEST COMPLETE")
print("="*70)
print()

if result.get('success') and result.get('live_url'):
    print("✅ Deployment works correctly!")
    print("✅ URL is returned as expected!")
    print()
    print("Your Streamlit app will work the same way:")
    print("1. Click 'Host Portfolio Online'")
    print("2. Wait for deployment (10-30 seconds)")
    print("3. Purple box appears with live URL")
    print("4. Click to open your portfolio")
else:
    print("❌ There's an issue with the deployment")
    print("   Please check the error messages above")
