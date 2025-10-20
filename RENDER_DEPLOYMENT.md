# 🚀 Render Deployment Guide

## Quick Deploy to Render

### Method 1: One-Click Deploy (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/samsanjay99/AI-Resume-Analyzer)

### Method 2: Manual Deployment

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/samsanjay99/AI-Resume-Analyzer.git
   cd AI-Resume-Analyzer
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `AI-Resume-Analyzer`

4. **Configure Service**
   - **Name**: `smart-ai-resume-analyzer`
   - **Environment**: `Docker`
   - **Plan**: `Free` (or paid for better performance)
   - **Dockerfile Path**: `./Dockerfile`

## 🔑 Environment Variables Configuration

In Render dashboard, add these environment variables:

### Required for AI Features:
```
GOOGLE_API_KEY = your_google_gemini_api_key
```

### Optional for Additional Models:
```
A4F_API_KEY = your_a4f_api_key
OPENROUTER_API_KEY = your_openrouter_api_key
```

### How to Get API Keys:

1. **Google Gemini API Key** (Free):
   - Visit: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in and create API key

2. **A4F API Key** (Optional):
   - Visit: [A4F API](https://api.a4f.co)
   - Sign up and get API key

## 📋 Deployment Steps

1. **Connect Repository**
   - In Render dashboard, click "New Web Service"
   - Connect your GitHub account
   - Select the `AI-Resume-Analyzer` repository

2. **Configure Build Settings**
   - **Name**: `smart-ai-resume-analyzer`
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`

3. **Add Environment Variables**
   - Go to "Environment" tab
   - Add your API keys as shown above

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (5-10 minutes)

## 🎯 Features Available After Deployment

### With Google API Key:
✅ AI Resume Analysis (Google Gemini)  
✅ AI Portfolio Generation  
✅ Smart Content Extraction  
✅ Advanced Resume Insights  

### With A4F API Key (Additional):
✅ 7 More AI Models:
- GPT 5 Nano
- Llama 3.2 1B
- Mistral Nemo
- Kimi K2
- Qwen3 4B Thinking
- Qwen2.5 Coder 3B
- Hunyuan A13B

### Always Available:
✅ Standard Resume Analysis  
✅ Resume Builder  
✅ Dashboard & Analytics  
✅ Feedback System  
✅ File Management  

## 🔧 Render-Specific Optimizations

The Dockerfile includes:
- **Dynamic Port Configuration** (`$PORT` environment variable)
- **Health Check Endpoint** for Render monitoring
- **Optimized Dependencies** for faster builds
- **NLTK Data Pre-download** for text processing
- **Proper Directory Structure** for file uploads

## 🚨 Troubleshooting

### Build Fails
- Check that all files are committed to GitHub
- Verify Dockerfile syntax
- Check build logs in Render dashboard

### App Won't Start
- Verify environment variables are set
- Check that port configuration is correct
- Review application logs

### AI Features Not Working
- Ensure `GOOGLE_API_KEY` is set in environment variables
- Verify API key is valid and active
- Check API quotas and limits

## 📊 Performance Tips

### Free Plan Limitations:
- App sleeps after 15 minutes of inactivity
- 512MB RAM limit
- Shared CPU

### Upgrade Benefits:
- Always-on service
- More RAM and CPU
- Faster response times
- Custom domains

## 🎉 Post-Deployment

After successful deployment:

1. **Test All Features**
   - Upload a resume for analysis
   - Try portfolio generation
   - Check admin dashboard

2. **Admin Access**
   - Email: `sam@gmail.com`
   - Password: `sanjay2026`

3. **Share Your App**
   - Your app will be available at: `https://your-app-name.onrender.com`

## 🔄 Updates and Maintenance

To update your deployed app:
1. Push changes to your GitHub repository
2. Render will automatically rebuild and deploy
3. Monitor build logs for any issues

## 📞 Support

If you encounter issues:
1. Check Render build and application logs
2. Verify environment variables are correctly set
3. Ensure API keys are valid and have sufficient quota
4. Review the troubleshooting section above

---

**Enjoy your Smart AI Resume Analyzer on Render! 🚀**