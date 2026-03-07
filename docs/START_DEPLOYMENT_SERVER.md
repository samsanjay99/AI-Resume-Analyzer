# Quick Start: Portfolio Deployment Server

## Overview

The portfolio deployment server is a standalone Flask application that handles portfolio hosting with real-time progress tracking.

## Prerequisites

1. **Python 3.8+** installed
2. **Netlify Account** (free tier works)
3. **Netlify Personal Access Token**

## Setup Steps

### 1. Get Netlify Token

1. Go to https://app.netlify.com/user/applications
2. Click "New access token"
3. Give it a name (e.g., "Portfolio Deployer")
4. Copy the generated token

### 2. Configure Environment

Add to your `.env` file:

```env
NETLIFY_TOKEN=your_token_here
```

### 3. Install Dependencies

```bash
pip install flask requests python-dotenv
```

Or use the requirements file:

```bash
pip install -r deploy_requirements.txt
```

### 4. Start the Server

```bash
python deploy_server.py
```

The server will start on `http://localhost:5001`

You should see:

```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

## Usage Flow

1. **Generate Portfolio** in Streamlit app
2. **Click "Host Portfolio Online"** button
3. **New tab opens** with deployment interface
4. **Watch real-time progress**:
   - 🔷 Preparing deployment...
   - 📁 Portfolio files extracted
   - 🔐 Authenticating with Netlify...
   - 📦 Creating deployment package...
   - 🚀 Uploading to Netlify...
   - 🌐 Configuring site...
   - ✅ Deployment completed successfully!
5. **Get live URL** - Copy and share!

## Features

### Beautiful UI
- Purple gradient background
- Modern card design
- Smooth animations
- Professional appearance

### Real-Time Progress
- Progress bar (0-100%)
- Live deployment logs
- Status updates every second
- Spinner animation

### Success Screen
- Confetti animation 🎉
- Live URL display
- Copy button
- Beautiful gradient card

## Troubleshooting

### Port Already in Use

If port 5001 is already in use:

```bash
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
python deploy_server.py --port 5002
```

### NETLIFY_TOKEN Not Found

Make sure:
1. `.env` file exists in project root
2. Token is correctly formatted: `NETLIFY_TOKEN=nfp_...`
3. No spaces around the `=` sign
4. Server was restarted after adding token

### Deployment Fails

Check:
1. Token is valid (not expired)
2. Portfolio ZIP file exists
3. Internet connection is working
4. Netlify service is up (check https://www.netlifystatus.com/)

### Browser Doesn't Open

If the new tab doesn't open automatically:
1. Check browser popup blocker settings
2. Manually open: `http://localhost:5001/?portfolio=/path/to/portfolio.zip`
3. Use the deployment URL shown in Streamlit

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 deploy_server:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY deploy_server.py .
COPY templates/ templates/
COPY deploy_requirements.txt .
COPY .env .

RUN pip install -r deploy_requirements.txt

EXPOSE 5001

CMD ["python", "deploy_server.py"]
```

Build and run:

```bash
docker build -t portfolio-deployer .
docker run -p 5001:5001 portfolio-deployer
```

### Environment Variables

For production, use environment variables instead of `.env`:

```bash
export NETLIFY_TOKEN=your_token_here
export FLASK_SECRET_KEY=your_secret_key_here
python deploy_server.py
```

## API Reference

### POST /deploy

Start a new deployment.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `portfolio` (ZIP file)

**Response:**
```json
{
  "deployment_id": "deploy_1234567890"
}
```

### GET /status/<deployment_id>

Get deployment status.

**Response:**
```json
{
  "status": "deploying",
  "progress": 60,
  "logs": ["🔷 Preparing...", "📁 Extracted..."],
  "live_url": null,
  "error": null
}
```

**Status Values:**
- `preparing` - Initial setup
- `deploying` - Deployment in progress
- `success` - Deployment completed
- `failed` - Deployment failed

## Security Notes

1. **Never commit** `.env` file to version control
2. **Rotate tokens** regularly
3. **Use HTTPS** in production
4. **Implement rate limiting** for public deployments
5. **Add authentication** if exposing publicly

## Support

For issues or questions:
1. Check `DEPLOYMENT_SERVER_GUIDE.md` for detailed documentation
2. Review `docs/ALGORITHMS_EXPLAINED.md` for technical details
3. Check Netlify API documentation: https://docs.netlify.com/api/get-started/

## Quick Commands

```bash
# Start server
python deploy_server.py

# Check if server is running
curl http://localhost:5001/

# Test deployment (with curl)
curl -X POST -F "portfolio=@portfolio.zip" http://localhost:5001/deploy

# Check deployment status
curl http://localhost:5001/status/deploy_1234567890
```

---

**Last Updated:** February 2026  
**Version:** 1.0
