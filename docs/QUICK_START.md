# 🚀 Quick Start Guide

Get Smart Resume AI up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (Neon recommended)
- Google Gemini API key
- Netlify token (optional, for portfolio hosting)

## Installation Steps

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-resume-ai.git
cd smart-resume-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Database (Required)
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require

# AI Services (Required)
GOOGLE_API_KEY=your_google_gemini_api_key

# Portfolio Hosting (Optional)
NETLIFY_TOKEN=your_netlify_token
```

**Get your API keys:**
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Neon Database**: https://neon.tech/ (free tier available)
- **Netlify**: https://app.netlify.com/user/applications

### 3. Initialize Database

```bash
python scripts/optimize_database_indexes.py
```

This will:
- Create all required tables
- Set up indexes for performance
- Create default admin account

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Default Login

**Admin Account:**
- Email: `admin@example.com`
- Password: `sanjay99`

**⚠️ Important:** Change these credentials after first login!

## First Steps

1. **Login** with the default admin credentials
2. **Upload a resume** to test the analysis
3. **Generate a portfolio** from your resume
4. **Explore the dashboard** to see analytics

## Features Overview

### For Users
- 📄 **Resume Analysis** - AI-powered resume scoring
- 🎨 **Portfolio Generator** - Convert resume to website
- 📝 **Resume Builder** - Create ATS-optimized resumes
- 💼 **Job Search** - Find relevant job opportunities
- 📚 **Learning Dashboard** - Get course recommendations

### For Admins
- 📊 **Analytics Dashboard** - User and system statistics
- 👥 **User Management** - View all users and activity
- 🔍 **System Monitoring** - Performance metrics
- 📈 **Reports** - Generate usage reports

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
**Solution:** Check your `DATABASE_URL` in `.env` file

### API Key Error
```
Error: GOOGLE_API_KEY not found
```
**Solution:** Add your Google Gemini API key to `.env` file

### Port Already in Use
```
Error: Address already in use
```
**Solution:** Run on a different port:
```bash
streamlit run app.py --server.port 8502
```

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed features
- Check [Admin Guide](ADMIN_GUIDE.md) for admin features
- See [Performance Guide](PERFORMANCE_GUIDE.md) for optimization

## Need Help?

- Check the [FAQ](FAQ.md)
- Open an issue on GitHub
- Contact support

---

**Ready to go!** 🎉 Start analyzing resumes and generating portfolios!
