# 🚀 Streamlit Cloud Configuration Guide

## 🔑 Required API Keys for Full Functionality

To use all features of the Smart AI Resume Analyzer on Streamlit Cloud, you need to configure API keys.

### 1. Google Gemini API Key (Required)

**Get your free API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

**Add to Streamlit Cloud:**
1. Go to your Streamlit Cloud app
2. Click "Settings" → "Secrets"
3. Add this line:
```
GOOGLE_API_KEY = "your_actual_api_key_here"
```

### 2. A4F API Key (Optional - for additional AI models)

**Get your API key:**
1. Go to [A4F API](https://api.a4f.co)
2. Sign up for an account
3. Get your API key from the dashboard

**Add to Streamlit Cloud:**
```
A4F_API_KEY = "your_a4f_api_key_here"
```

## 🎯 What Each API Key Enables

### With Google Gemini API Key:
✅ AI Resume Analysis  
✅ Portfolio Generation  
✅ Advanced Resume Insights  
✅ Smart Content Extraction  

### With A4F API Key (Additional):
✅ 7 Additional AI Models:
- GPT 5 Nano
- Llama 3.2 1B  
- Mistral Nemo
- Kimi K2
- Qwen3 4B Thinking
- Qwen2.5 Coder 3B
- Hunyuan A13B

### Without API Keys:
✅ Standard Resume Analysis  
✅ Resume Builder  
✅ Dashboard & Analytics  
✅ Feedback System  
✅ File Management  
❌ AI-Powered Analysis  
❌ Portfolio Generation  

## 🔧 Complete Streamlit Cloud Secrets Configuration

In your Streamlit Cloud app settings → Secrets, add:

```toml
# Required for AI features
GOOGLE_API_KEY = "your_google_gemini_api_key"

# Optional for additional AI models  
A4F_API_KEY = "your_a4f_api_key"

# Optional for future features
OPENROUTER_API_KEY = "your_openrouter_api_key"
```

## 🚨 Troubleshooting

### Issue: "No API Keys Configured" message
**Solution:** Add the `GOOGLE_API_KEY` to your Streamlit Cloud secrets

### Issue: Only "Google Gemini" model available
**Solution:** Add the `A4F_API_KEY` to unlock additional models

### Issue: Portfolio generation fails
**Solution:** Ensure `GOOGLE_API_KEY` is properly configured

## 📞 Support

If you need help:
1. Check that API keys are correctly added to Streamlit Cloud secrets
2. Verify API keys are valid and active
3. Restart your Streamlit Cloud app after adding secrets

## 🎉 After Configuration

Once API keys are configured, you'll have access to:
- 🤖 **8 AI Models** for resume analysis
- 🌐 **AI Portfolio Generation** 
- 📊 **Advanced Analytics**
- 🎯 **Smart Recommendations**

Enjoy your fully-featured Smart AI Resume Analyzer! 🚀