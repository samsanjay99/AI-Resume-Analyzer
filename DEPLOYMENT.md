# 🚀 Deployment Guide

## Quick Deploy Options

### 1. Streamlit Cloud (Recommended)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `samsanjay99/AI-Resume-Analyzer`
4. Set main file path: `app.py`
5. Click "Deploy"

### 2. Heroku Deployment
```bash
# Install Heroku CLI first
heroku create your-app-name
git push heroku main
```

### 3. Render Deployment (Recommended for Docker)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/samsanjay99/AI-Resume-Analyzer)

**Manual Steps:**
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Select Docker environment
5. Add environment variables

**See detailed guide:** [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

### 4. Railway Deployment
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy automatically

### 4. Local Development
```bash
# Clone repository
git clone https://github.com/samsanjay99/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer

# Install dependencies
pip install -r requirements.txt

# Setup deployment
python deploy.py

# Run application
streamlit run app.py
```

## Environment Variables

For deployment platforms, set these environment variables:

```
GOOGLE_API_KEY=your_google_gemini_api_key
A4F_API_KEY=your_a4f_api_key (optional)
```

## Admin Access

- **Email**: sam@gmail.com
- **Password**: sanjay2026

## Features

✅ **Complete SQLite Database**
✅ **Admin Dashboard with Analytics**
✅ **Feedback System Integration**
✅ **File Upload Tracking**
✅ **AI-Powered Resume Analysis**
✅ **Portfolio Generation**
✅ **Job Search Integration**

## Support

For issues or questions, please create an issue on GitHub.