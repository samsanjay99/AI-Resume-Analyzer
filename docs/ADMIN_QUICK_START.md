# Admin Dashboard - Quick Start Guide

## Access the Enhanced Dashboard

### Step 1: Login as Admin
```
Email: sam@gmail.com
Password: sanjay2026
```

### Step 2: Navigate to Dashboard
- Click "📊 DASHBOARD" in the sidebar
- Dashboard loads with overview metrics

### Step 3: Explore the 4 Tabs

## Tab Overview

### 📊 Resume Data
**What it shows**: All resume submissions with analysis scores

**Actions you can take**:
- Filter by target role (dropdown 1)
- Filter by category (dropdown 2)
- Download filtered data (Excel)
- Download all data (Excel)
- View admin activity logs
- Download admin logs (Excel)

**Use case**: Review all resume submissions and their scores

---

### 👥 User Management
**What it shows**: Complete user directory with statistics

**Columns displayed**:
- Email
- Full Name
- Registration Date
- Last Login
- Active Status
- Total Resumes
- Total Analyses
- Total AI Analyses
- Average ATS Score
- Average AI Score

**Filters available**:
1. **Status**: All / Active / Inactive
2. **Activity**: All / Has Resumes / No Resumes
3. **Sort by**: Created Date / Last Login / Total Resumes / Avg Score

**Actions you can take**:
- Filter users by status and activity
- Sort by different metrics
- Download user data (Excel)

**Use cases**:
- Find inactive users
- Identify power users
- Track user engagement
- Export user list for reporting

---

### 📊 System Analytics
**What it shows**: Platform-wide statistics and trends

**Key Metrics** (top row):
1. **Total Users** - with monthly growth indicator
2. **Active Users (30d)** - with percentage of total
3. **Total Resumes** - across all users
4. **Total Analyses** - standard + AI combined

**Charts**:
1. **User Growth (Last 7 Days)** - Line chart showing new registrations
2. **Platform Activity (Last 7 Days)** - Bar chart showing resumes created

**Use cases**:
- Monitor platform growth
- Track user acquisition
- Identify activity trends
- Measure platform health

---

### 🎯 Engagement Metrics
**What it shows**: User engagement patterns and analysis usage

**Visualizations**:
1. **User Activity Distribution** (Pie Chart)
   - Inactive: 0 resumes
   - Low Activity: 1-2 resumes
   - Medium Activity: 3-5 resumes
   - High Activity: 6+ resumes

2. **Analysis Type Distribution** (Bar Chart)
   - Standard Analysis count
   - AI Analysis count

3. **Top 10 Most Active Users** (Table)
   - Email
   - Full Name
   - Total Resumes
   - Total Analyses

**Use cases**:
- Identify engagement levels
- Find power users for testimonials
- Track AI vs standard analysis adoption
- Spot inactive users for re-engagement

---

## Common Tasks

### Task 1: Find All Active Users
1. Go to "👥 User Management" tab
2. Set Status filter to "Active"
3. Click "📥 Download User Data"

### Task 2: Identify Power Users
1. Go to "👥 User Management" tab
2. Set Sort by to "Total Resumes"
3. Top users appear first
4. OR go to "🎯 Engagement Metrics" tab
5. Check "Top 10 Most Active Users" table

### Task 3: Monitor Platform Growth
1. Go to "📊 System Analytics" tab
2. Check "Total Users" metric for monthly growth
3. Review "User Growth (Last 7 Days)" chart
4. Check "Platform Activity" chart for usage trends

### Task 4: Export All Resume Data
1. Go to "📊 Resume Data" tab
2. Set filters to "All" (or apply specific filters)
3. Click "📥 Download All Data"
4. Excel file downloads with timestamp

### Task 5: Check User Engagement
1. Go to "🎯 Engagement Metrics" tab
2. Review pie chart for activity distribution
3. Check if most users are active or inactive
4. Review top users table

---

## Troubleshooting

### Dashboard won't load
- Check internet connection
- Verify database connection in .env
- Clear browser cache (Ctrl+Shift+Delete)
- Refresh page (Ctrl+Shift+R)

### Filters not working
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Try different browser

### Download button not working
- Check browser download settings
- Allow downloads from the site
- Try different browser

### Charts not displaying
- Ensure plotly is installed
- Check if data exists for time period
- Refresh the page

### "No users found" message
- Verify users table has data
- Check database connection
- Run test: `python test_enhanced_dashboard.py`

---

## Tips & Best Practices

### Daily Tasks
- Check "Total Users" for new registrations
- Review "Active Users (30d)" percentage
- Monitor "Platform Activity" chart

### Weekly Tasks
- Export user data for backup
- Review top 10 active users
- Check engagement distribution
- Identify inactive users

### Monthly Tasks
- Export all resume data
- Analyze user growth trends
- Review analysis type adoption
- Plan re-engagement campaigns

### Data Export
- All exports include timestamp in filename
- Excel format (.xlsx) for easy analysis
- Filtered exports only include visible data
- All data exports include everything

---

## Quick Reference

### Keyboard Shortcuts
- `Ctrl+Shift+R` - Hard refresh
- `Ctrl+Shift+Delete` - Clear cache
- `Ctrl+F` - Find on page

### Admin Credentials
```
Email: sam@gmail.com
Password: sanjay2026
```

### Support Files
- `ENHANCED_DASHBOARD_GUIDE.md` - Detailed guide
- `DASHBOARD_ENHANCEMENT_COMPLETE.md` - Technical details
- `test_enhanced_dashboard.py` - Test script

### Test Command
```bash
python test_enhanced_dashboard.py
```

---

**Last Updated**: March 5, 2026
**Dashboard Version**: 2.0 (Multi-User Enhanced)
