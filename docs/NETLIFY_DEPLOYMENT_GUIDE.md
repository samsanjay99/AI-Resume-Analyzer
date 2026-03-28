# Netlify Deployment - Simple & Reliable

## Why Netlify?

✅ **Instant deployment** - No waiting for GitHub Pages to build  
✅ **Automatic HTTPS** - Secure by default  
✅ **Global CDN** - Fast worldwide  
✅ **Simple API** - One POST request  
✅ **Free tier** - Perfect for portfolios  

## Setup (5 Minutes)

### Step 1: Get Netlify Token

1. Create free account at https://netlify.com
2. Go to https://app.netlify.com/user/applications#personal-access-tokens
3. Click "New access token"
4. Name it "Portfolio Deployer"
5. Copy the token: `nfp_...`

### Step 2: Add to .env

```env
NETLIFY_TOKEN=YOUR_NETLIFY_TOKEN
```

### Step 3: Install Dependencies

```bash
pip install requests python-dotenv
```

## Implementation

### 1. Helper Functions (Already Added)

```python
def save_portfolio_to_folder(files_dict):
    """Convert portfolio files dict to a real folder"""
    temp_dir = tempfile.mkdtemp(prefix="portfolio_")
    
    for path, content in files_dict.items():
        full_path = os.path.join(temp_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return temp_dir


def deploy_to_netlify(folder_path):
    """Deploy portfolio folder to Netlify"""
    import requests
    import zipfile
    import io
    
    token = os.getenv("NETLIFY_TOKEN")
    
    if not token:
        return {
            "success": False,
            "error": "NETLIFY_TOKEN not found"
        }
    
    # Create ZIP
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                z.write(full_path, rel_path)
    
    zip_buffer.seek(0)
    
    # Deploy to Netlify
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }
    
    response = requests.post(
        "https://api.netlify.com/api/v1/sites",
        headers=headers,
        data=zip_buffer.read(),
        timeout=120
    )
    
    if response.status_code in (200, 201):
        data = response.json()
        return {
            "success": True,
            "live_url": data.get("url"),
            "admin_url": data.get("admin_url"),
            "site_id": data.get("id")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }
```

### 2. Button Implementation

```python
if st.button("🚀 Host Portfolio Online"):
    if not os.getenv("NETLIFY_TOKEN"):
        st.error("❌ NETLIFY_TOKEN not found")
    else:
        with st.spinner("🚀 Deploying to Netlify..."):
            # Extract files from ZIP
            portfolio_files = {}
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    with zip_ref.open(file_name) as file:
                        content = file.read().decode('utf-8', errors='ignore')
                        portfolio_files[file_name] = content
            
            # Save to folder
            folder_path = save_portfolio_to_folder(portfolio_files)
            
            # Deploy
            result = deploy_to_netlify(folder_path)
            
            # Store result
            st.session_state.deployment_result = result
            
            # Cleanup
            import shutil
            shutil.rmtree(folder_path, ignore_errors=True)
```

### 3. Display Result

```python
if st.session_state.deployment_result:
    result = st.session_state.deployment_result
    
    if result.get('success'):
        st.success("🎉 Portfolio deployed!")
        st.code(result["live_url"])
        st.info("💡 Your site is live immediately with HTTPS!")
    else:
        st.error(f"❌ Failed: {result.get('error')}")
```

## Testing

### 1. Check Token

```python
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("NETLIFY_TOKEN"))
```

Should print: `nfp_...`

### 2. Test Deployment

1. Generate a portfolio
2. Click "🚀 Host Portfolio Online"
3. Wait 5-10 seconds
4. See live URL
5. Click URL → Portfolio loads instantly!

## Expected Flow

```
User clicks button
    ↓
Spinner: "🚀 Deploying to Netlify..."
    ↓
Extract files from ZIP
    ↓
Save to temp folder
    ↓
Create ZIP of folder
    ↓
POST to Netlify API
    ↓
Get response with URL
    ↓
Store in session_state
    ↓
Display success message
    ↓
Show live URL
    ↓
URL persists across reruns ✅
```

## Advantages Over GitHub Pages

| Feature | Netlify | GitHub Pages |
|---------|---------|--------------|
| Deploy Time | 5-10 seconds | 1-2 minutes |
| HTTPS | Automatic | Automatic |
| Custom Domain | Free | Free |
| Build Process | Not needed | Jekyll build |
| API Complexity | Simple | Complex |
| Repository | Not needed | Required |

## Common Issues

### Issue: "NETLIFY_TOKEN not found"

**Solution:**
1. Check `.env` file exists in project root
2. Verify token is correct: `NETLIFY_TOKEN=nfp_...`
3. Restart Streamlit app
4. Check with: `print(os.getenv("NETLIFY_TOKEN"))`

### Issue: "index.html not found"

**Solution:**
Netlify requires `index.html` at root. Verify portfolio files include:
```
index.html  ← MUST exist
main.css
assets/
  img/
  js/
```

### Issue: "Deployment timeout"

**Solution:**
1. Check internet connection
2. Verify Netlify API is accessible
3. Try smaller portfolio (reduce images)
4. Increase timeout: `timeout=180`

### Issue: "Invalid token"

**Solution:**
1. Generate new token at Netlify
2. Update `.env` file
3. Restart app

## Netlify Dashboard

After deployment, visit admin URL to:
- View deployment logs
- Configure custom domain
- Set up redirects
- Enable form handling
- View analytics

## Production Tips

### 1. Error Handling

```python
try:
    result = deploy_to_netlify(folder_path)
except requests.exceptions.Timeout:
    result = {"success": False, "error": "Deployment timeout"}
except Exception as e:
    result = {"success": False, "error": str(e)}
```

### 2. Progress Indication

```python
with st.spinner("🚀 Deploying to Netlify..."):
    st.write("📦 Preparing files...")
    folder_path = save_portfolio_to_folder(portfolio_files)
    
    st.write("🚀 Uploading to Netlify...")
    result = deploy_to_netlify(folder_path)
    
    st.write("✅ Deployment complete!")
```

### 3. Cleanup

```python
import shutil
import atexit

# Cleanup temp folders on exit
def cleanup_temp_folders():
    temp_dir = tempfile.gettempdir()
    for folder in os.listdir(temp_dir):
        if folder.startswith("portfolio_"):
            shutil.rmtree(os.path.join(temp_dir, folder), ignore_errors=True)

atexit.register(cleanup_temp_folders)
```

## Security

✅ **Token in .env** - Never hardcode  
✅ **Add to .gitignore** - Don't commit token  
✅ **Use environment variables** - For production  
✅ **Rotate tokens** - Periodically update  

## Conclusion

Netlify deployment is:
- ✅ Simple (one API call)
- ✅ Fast (5-10 seconds)
- ✅ Reliable (99.9% uptime)
- ✅ Free (generous limits)
- ✅ Professional (HTTPS, CDN)

Perfect for portfolio hosting!
