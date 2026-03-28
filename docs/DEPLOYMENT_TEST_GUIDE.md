# Portfolio Deployment - Testing Guide

## Issue Fixed

The "Host Portfolio Online" button was causing page rerun without opening the deployment page.

## Solution

Changed from JavaScript `window.open()` to a persistent HTML link that:
- ✅ Survives page reruns
- ✅ Opens in new tab when clicked
- ✅ Shows clear instructions
- ✅ Provides visual feedback

---

## How to Test

### Step 1: Start the Deployment Server

Open a **new terminal** and run:

```bash
python deploy_server.py
```

You should see:
```
* Running on http://127.0.0.1:5001
```

**Keep this terminal open!** The server must be running for deployment to work.

### Step 2: Generate a Portfolio

1. Go to your Streamlit app
2. Navigate to "Portfolio Generator"
3. Upload a resume or fill in the form
4. Click "Generate Portfolio"
5. Wait for portfolio generation to complete

### Step 3: Click "Host Portfolio Online"

1. After portfolio is generated, you'll see two buttons:
   - 📥 Download Portfolio (.zip)
   - 🚀 Host Portfolio Online

2. Click "🚀 Host Portfolio Online"

3. You should see a **purple gradient box** appear with:
   - Title: "🚀 Deploy Your Portfolio"
   - Button: "Open Deployment Page →"

### Step 4: Open Deployment Page

1. Click the **"Open Deployment Page →"** button in the purple box
2. A new tab will open with the deployment interface
3. The deployment will start automatically

### Step 5: Watch Deployment Progress

In the new tab, you'll see:
- Real-time progress bar (0% → 100%)
- Live deployment logs:
  - 🔷 Preparing deployment...
  - 📁 Portfolio files extracted
  - 🔐 Authenticating with Netlify...
  - 📦 Creating deployment package...
  - 🚀 Uploading to Netlify...
  - 🌐 Configuring site...
  - ✅ Deployment completed successfully!

### Step 6: Get Your Live URL

Once deployment completes:
- Confetti animation plays 🎉
- Live URL is displayed
- You can copy and share the URL

---

## Troubleshooting

### Issue: "Connection refused" or "Cannot connect"

**Cause:** Deployment server is not running

**Solution:**
```bash
# Start the deployment server in a new terminal
python deploy_server.py
```

### Issue: Button doesn't appear after clicking "Host Portfolio Online"

**Cause:** NETLIFY_TOKEN not configured

**Solution:**
1. Get a Netlify Personal Access Token from https://app.netlify.com/user/applications
2. Add to your `.env` file:
   ```
   NETLIFY_TOKEN=your_token_here
   ```
3. Restart the Streamlit app

### Issue: Purple box appears but link doesn't work

**Cause:** Deployment server not running on port 5001

**Solution:**
1. Check if server is running: `netstat -ano | findstr :5001`
2. If not running, start it: `python deploy_server.py`
3. If port is in use, kill the process or use a different port

### Issue: Deployment page opens but shows error

**Cause:** Portfolio ZIP file not found or invalid

**Solution:**
1. Make sure portfolio was generated successfully
2. Check that the ZIP file exists in `generated_portfolios/`
3. Try generating the portfolio again

---

## Expected Flow

```
1. User clicks "🚀 Host Portfolio Online"
   ↓
2. Purple gradient box appears with link
   ↓
3. User clicks "Open Deployment Page →"
   ↓
4. New tab opens: http://localhost:5001/?portfolio=...
   ↓
5. Deployment page loads
   ↓
6. Deployment starts automatically
   ↓
7. Progress bar and logs update in real-time
   ↓
8. Deployment completes
   ↓
9. Live URL displayed with confetti 🎉
```

---

## Visual Guide

### Before Clicking Button:
```
┌─────────────────────────────────────┐
│  📥 Download Portfolio (.zip)       │
│  🚀 Host Portfolio Online           │
└─────────────────────────────────────┘
```

### After Clicking Button:
```
┌─────────────────────────────────────┐
│  📥 Download Portfolio (.zip)       │
│  🚀 Host Portfolio Online           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ✅ Ready to deploy!                │
│                                     │
│  ╔═══════════════════════════════╗ │
│  ║  🚀 Deploy Your Portfolio     ║ │
│  ║                               ║ │
│  ║  [Open Deployment Page →]    ║ │
│  ║                               ║ │
│  ║  Click the button above to    ║ │
│  ║  open the deployment          ║ │
│  ║  interface in a new tab       ║ │
│  ╚═══════════════════════════════╝ │
│                                     │
│  ℹ️ What happens next:              │
│  1. Click the button above          │
│  2. Deployment page opens           │
│  3. Real-time progress shown        │
│  4. Get live URL                    │
└─────────────────────────────────────┘
```

---

## Configuration

### .env File

Make sure your `.env` file contains:

```env
# Netlify Configuration
NETLIFY_TOKEN=YOUR_NETLIFY_TOKEN_token_here
```

### Port Configuration

Default port: `5001`

To change port, edit `deploy_server.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)  # Change 5001 to your port
```

---

## Quick Test Commands

```bash
# Terminal 1: Start deployment server
python deploy_server.py

# Terminal 2: Start Streamlit app
streamlit run app.py

# Check if deployment server is running
curl http://localhost:5001/

# Check if port is in use
netstat -ano | findstr :5001
```

---

## Success Indicators

✅ Deployment server shows: `Running on http://127.0.0.1:5001`  
✅ Purple gradient box appears after clicking button  
✅ Link opens in new tab  
✅ Deployment page loads successfully  
✅ Progress bar updates in real-time  
✅ Live URL displayed after completion  

---

## Notes

- The deployment server must be running **before** clicking the host button
- The link persists across page reloads (stored in session state)
- Click "🔄 Reset" to generate a new deployment link
- Each portfolio generation creates a new ZIP file with a unique path

---

**Status**: ✅ Fixed and Ready to Test  
**Last Updated**: February 24, 2026
