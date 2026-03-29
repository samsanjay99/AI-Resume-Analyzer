# GitHub Portfolio Hosting Setup Guide

## Overview

This guide explains how to set up automatic portfolio hosting using GitHub Pages. Users can click a "Host Portfolio" button and get a live URL instantly!

---

## 🎯 How It Works

1. User generates a portfolio in the app
2. Clicks "🚀 Host Portfolio" button
3. System automatically:
   - Creates a GitHub repository
   - Uploads portfolio files
   - Enables GitHub Pages
   - Returns live URL
4. Portfolio is live at: `https://username.github.io/portfolio-name`

---

## 📋 Setup Steps

### Step 1: Create GitHub Service Account

1. **Create a new GitHub account** (or use existing):
   - Go to https://github.com/signup
   - Username suggestion: `smart-resume-portfolios` or `your-app-portfolios`
   - Use a dedicated email for this account

2. **Verify the email** and complete setup

### Step 2: Generate GitHub Personal Access Token

1. **Login to the GitHub account** you just created

2. **Go to Settings**:
   - Click your profile picture (top right)
   - Click "Settings"

3. **Navigate to Developer Settings**:
   - Scroll down in left sidebar
   - Click "Developer settings"

4. **Create Personal Access Token**:
   - Click "Personal access tokens"
   - Click "Tokens (classic)"
   - Click "Generate new token (classic)"

5. **Configure Token**:
   - **Note**: `Smart Resume Portfolio Hosting`
   - **Expiration**: `No expiration` (or set to 1 year)
   - **Select scopes**: Check these boxes:
     - ✅ `repo` (Full control of private repositories)
       - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
     - ✅ `delete_repo` (Delete repositories) - Optional, for cleanup

6. **Generate and Copy Token**:
   - Click "Generate token" at bottom
   - **IMPORTANT**: Copy the token immediately (starts with `ghp_...`)
   - You won't be able to see it again!

### Step 3: Add Token to Environment Variables

1. **Open `.env` file** in your project root

2. **Add GitHub configuration**:
   ```env
   # GitHub Configuration (for portfolio hosting)
   GITHUB_TOKEN=ghp_your_actual_token_here
   GITHUB_USERNAME=smart-resume-portfolios
   ```

3. **Replace values**:
   - `GITHUB_TOKEN`: Paste the token you copied
   - `GITHUB_USERNAME`: Your GitHub account username

4. **Save the file**

### Step 4: Test the Setup

Run the test script to verify everything works:

```bash
python utils/github_deployer.py
```

If successful, you'll see:
```json
{
  "success": true,
  "repo_name": "portfolio-test-user-20260222123456",
  "repo_url": "https://github.com/smart-resume-portfolios/portfolio-test-user-20260222123456",
  "live_url": "https://smart-resume-portfolios.github.io/portfolio-test-user-20260222123456",
  "message": "Portfolio deployed successfully! It may take 1-2 minutes to be live."
}
```

---

## 🔒 Security Best Practices

### Protect Your Token

1. **Never commit `.env` to Git**:
   - Already in `.gitignore`
   - Double-check before pushing

2. **Use environment variables in production**:
   - Streamlit Cloud: Add to Secrets
   - Render: Add to Environment Variables
   - Heroku: Use Config Vars

3. **Rotate tokens periodically**:
   - Generate new token every 6-12 months
   - Delete old tokens

### Token Permissions

The token only needs:
- ✅ `repo` scope - Create and manage repositories
- ❌ No admin access
- ❌ No access to other accounts
- ❌ No billing access

---

## 🚀 Usage in Application

### For Users

1. Generate portfolio in the app
2. Click "🚀 Host Portfolio" button
3. Wait 5-10 seconds
4. Get live URL
5. Share the URL with anyone!

### Portfolio URLs

Format: `https://username.github.io/portfolio-name-timestamp`

Example:
- `https://smart-resume-portfolios.github.io/portfolio-john-doe-20260222123456`

### Features

- ✅ Free hosting forever
- ✅ HTTPS enabled by default
- ✅ Fast global CDN
- ✅ No bandwidth limits
- ✅ Custom domains supported (user can add later)
- ✅ Automatic updates if re-deployed

---

## 🛠️ Troubleshooting

### Error: "GitHub token not configured"

**Solution**: Add `GITHUB_TOKEN` to `.env` file

### Error: "Failed to create repository"

**Possible causes**:
1. Token expired - Generate new token
2. Token lacks permissions - Ensure `repo` scope is checked
3. Repository name conflict - System auto-generates unique names

### Error: "Failed to enable GitHub Pages"

**Solution**: 
- Wait 30 seconds and try again
- GitHub Pages may take time to initialize

### Portfolio not loading

**Wait time**: GitHub Pages takes 1-2 minutes to build and deploy

**Check**:
1. Visit the repository URL first
2. Check if files are uploaded
3. Wait 2 minutes, then try live URL

---

## 📊 Limitations

### GitHub Free Tier

- ✅ Unlimited public repositories
- ✅ Unlimited GitHub Pages sites
- ✅ 1 GB storage per repository
- ✅ 100 GB bandwidth per month (per site)

### Rate Limits

- **API calls**: 5,000 per hour (authenticated)
- **Repository creation**: No specific limit
- **File uploads**: 100 MB per file max

For typical portfolio usage, these limits are more than sufficient.

---

## 🔄 Alternative: User's Own GitHub Account

If you want users to host on their own GitHub accounts:

### Pros:
- Portfolios in user's account
- User has full control
- No central account needed

### Cons:
- Users need GitHub account
- Users need to generate token
- More complex for users

### Implementation:

1. Add GitHub login button
2. Request user's GitHub token
3. Store token securely (encrypted)
4. Deploy to user's account

---

## 📝 Example Deployment Flow

```python
from utils.github_deployer import GitHubDeployer

# Initialize deployer
deployer = GitHubDeployer()

# Portfolio files
portfolio_files = {
    'index.html': '<html>...</html>',
    'style.css': 'body { ... }',
    'script.js': 'console.log("Hello");'
}

# Deploy
result = deployer.deploy_portfolio(
    portfolio_files=portfolio_files,
    candidate_name='John Doe'
)

if result['success']:
    print(f"Live URL: {result['live_url']}")
    print(f"Repository: {result['repo_url']}")
else:
    print(f"Error: {result['error']}")
```

---

## 🎨 UI Integration

The "Host Portfolio" button will be added to the Portfolio Generator page:

```
┌─────────────────────────────────────┐
│  Portfolio Generated Successfully!  │
├─────────────────────────────────────┤
│                                     │
│  [📥 Download ZIP]  [🚀 Host Now]  │
│                                     │
└─────────────────────────────────────┘
```

When clicked:
1. Shows loading spinner
2. Deploys to GitHub
3. Shows success message with URL
4. Provides clickable link

---

## 💡 Tips

### Repository Naming

Format: `portfolio-{name}-{timestamp}`
- Ensures unique names
- Easy to identify
- Sortable by date

### Cleanup

To delete old portfolios:
```python
deployer.delete_repository('portfolio-name-timestamp')
```

Consider adding:
- Admin panel to view all portfolios
- Bulk delete option
- Auto-delete after 30 days (optional)

### Custom Domains

Users can add custom domains later:
1. Go to repository settings
2. Add custom domain
3. Configure DNS

---

## 📚 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

---

## ✅ Checklist

Before going live:

- [ ] GitHub account created
- [ ] Personal access token generated
- [ ] Token added to `.env` file
- [ ] Test deployment successful
- [ ] Token secured (not in Git)
- [ ] Production environment variables set
- [ ] UI button added
- [ ] Error handling implemented
- [ ] User documentation created

---

**Setup Time**: ~10 minutes  
**Cost**: $0 (completely free)  
**Maintenance**: Minimal (token rotation every 6-12 months)

---

This setup enables instant, free portfolio hosting for all your users!
