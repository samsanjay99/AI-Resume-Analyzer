# 📁 Project Structure

Complete overview of the Smart Resume AI project structure.

## Root Directory

```
smart-resume-ai/
├── app.py                          # Main Streamlit application
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
│
├── auth/                          # Authentication system
│   ├── auth_manager.py           # Authentication logic
│   ├── login_page.py             # Login UI
│   └── profile_page.py           # User profile page
│
├── config/                        # Configuration & optimization
│   ├── database.py               # Database connection & queries
│   ├── user_data_manager.py     # User data operations
│   ├── analysis_manager.py      # Analysis data management
│   ├── profile_manager.py       # Profile management
│   ├── course_recommendation_manager.py  # Course recommendations
│   ├── performance_optimizer.py  # Performance layer
│   ├── security_validator.py    # Security & validation
│   ├── app_initializer.py       # App initialization
│   ├── courses.py               # Course data
│   ├── job_roles.py             # Job role definitions
│   └── portfolio_placeholders.py # Portfolio templates
│
├── utils/                         # Utility modules
│   ├── ai_resume_analyzer.py    # AI analysis engine
│   ├── resume_builder.py        # Resume generation
│   ├── resume_analyzer.py       # Resume parsing
│   ├── portfolio_generator.py   # Portfolio creation
│   └── file_utils.py            # File operations
│
├── pages/                         # Additional Streamlit pages
│   ├── user_history.py          # User activity history
│   ├── learning_dashboard.py   # Course recommendations
│   └── profile_management.py   # Profile settings
│
├── dashboard/                     # Admin dashboard
│   └── dashboard.py             # Admin analytics & management
│
├── feedback/                      # Feedback system
│   └── feedback.py              # User feedback collection
│
├── jobs/                          # Job search
│   └── job_search.py            # Job search functionality
│
├── ui_components.py              # Reusable UI components
│
├── assets/                        # Static assets
│   ├── logo.jpg                 # Application logo
│   └── 124852522.jpeg          # Additional images
│
├── resume-to-portfoliov2/        # Portfolio templates
│   ├── index.html               # Main template
│   ├── main.css                 # Styles
│   ├── assets/                  # Template assets
│   │   ├── js/                  # JavaScript files
│   │   └── img/                 # Images
│   ├── creative-portfolio/      # Creative template
│   ├── dark-developer-portfolio/ # Dark theme template
│   └── professional-portfolio/  # Professional template
│
├── docs/                          # Documentation
│   ├── QUICK_START.md           # Quick start guide
│   ├── USER_GUIDE.md            # User documentation
│   ├── ADMIN_GUIDE.md           # Admin documentation
│   ├── PERFORMANCE_GUIDE.md     # Performance optimization
│   ├── PROJECT_STRUCTURE.md     # This file
│   └── [other documentation]
│
├── tests/                         # Test files
│   ├── test_multiuser_auth.py   # Auth tests
│   ├── test_user_history.py     # History tests
│   ├── test_analysis_storage.py # Analysis tests
│   └── [other test files]
│
└── scripts/                       # Utility scripts
    ├── optimize_database_indexes.py  # Database optimization
    ├── create_multiuser_schema.py    # Schema creation
    ├── migrate_sqlite_to_neon.py     # Database migration
    └── [other scripts]
```

## Key Files Explained

### Core Application

**`app.py`**
- Main Streamlit application entry point
- Handles routing and page rendering
- Integrates all modules

**`ui_components.py`**
- Reusable UI components
- Styling functions
- Common layouts

### Authentication (`auth/`)

**`auth_manager.py`**
- User authentication logic
- Session management
- Password hashing
- Admin verification

**`login_page.py`**
- Login and signup UI
- Form validation
- Error handling

**`profile_page.py`**
- User profile display
- Profile editing
- Settings management

### Configuration (`config/`)

**`database.py`**
- PostgreSQL connection pooling
- Database queries
- Schema initialization
- Performance optimization

**`performance_optimizer.py`**
- Caching layer (TTL-based)
- Lazy loading
- Performance monitoring
- Retry mechanisms

**`security_validator.py`**
- Input validation
- SQL injection protection
- XSS prevention
- Rate limiting

**`app_initializer.py`**
- Application startup
- Lazy-loaded components
- Health checks
- Environment validation

### Utilities (`utils/`)

**`ai_resume_analyzer.py`**
- AI-powered resume analysis
- Multiple AI model support
- Score calculation
- Recommendations generation

**`resume_builder.py`**
- Resume generation
- Template rendering
- PDF/DOCX export
- ATS optimization

**`portfolio_generator.py`**
- Portfolio website generation
- Template customization
- Netlify deployment
- Preview generation

### Pages (`pages/`)

**`user_history.py`**
- Activity timeline
- File management
- Deployment tracking
- Analytics

**`learning_dashboard.py`**
- Course recommendations
- Skill gap analysis
- Learning paths
- Progress tracking

### Dashboard (`dashboard/`)

**`dashboard.py`**
- Admin analytics
- User management
- System monitoring
- Report generation

## Data Flow

### Resume Analysis Flow
```
User Upload → File Processing → AI Analysis → Score Calculation → 
Database Storage → Results Display → History Tracking
```

### Portfolio Generation Flow
```
Resume Upload → Data Extraction → Template Selection → 
HTML Generation → Preview Display → ZIP Creation → 
Netlify Deployment (optional) → History Tracking
```

### Authentication Flow
```
Login Request → Credential Validation → Session Creation → 
Database Verification → Access Grant → Activity Logging
```

## Database Schema

### Main Tables
- `users` - User accounts
- `resume_data` - Resume information
- `resume_analysis` - Analysis results
- `ai_analysis` - AI analysis data
- `uploaded_files` - File tracking
- `portfolio_deployments` - Deployment history
- `course_recommendations` - Learning recommendations
- `user_profiles` - Extended user data
- `admin` - Admin accounts
- `admin_logs` - Admin activity
- `feedback` - User feedback

## Environment Variables

Required in `.env`:
```env
DATABASE_URL=postgresql://...
GOOGLE_API_KEY=...
NETLIFY_TOKEN=...
```

Optional:
```env
OPENROUTER_API_KEY=...
A4F_API_KEY=...
```

## Dependencies

### Core
- `streamlit` - Web framework
- `psycopg2` - PostgreSQL adapter
- `python-dotenv` - Environment variables

### AI & Analysis
- `google-generativeai` - Google Gemini
- `openai` - OpenAI API
- `pdfplumber` - PDF parsing

### Document Generation
- `python-docx` - DOCX creation
- `reportlab` - PDF generation
- `Pillow` - Image processing

### Utilities
- `requests` - HTTP requests
- `pandas` - Data manipulation
- `plotly` - Visualizations

## Development Workflow

1. **Local Development**
   ```bash
   streamlit run app.py
   ```

2. **Testing**
   ```bash
   python -m pytest tests/
   ```

3. **Database Optimization**
   ```bash
   python scripts/optimize_database_indexes.py
   ```

4. **Deployment**
   - Push to GitHub
   - Deploy to Streamlit Cloud/Render/Railway

## Performance Optimizations

### Implemented
- ✅ Connection pooling (2-20 connections)
- ✅ Query caching (5-minute TTL)
- ✅ Lazy loading components
- ✅ Database indexes (13 indexes)
- ✅ Batch operations
- ✅ Retry mechanisms

### Monitoring
- Performance metrics in admin panel
- Slow operation logging (>1s)
- Cache hit rate tracking
- Database query monitoring

## Security Features

### Implemented
- ✅ Input validation (email, phone, URL)
- ✅ SQL injection protection
- ✅ XSS prevention
- ✅ Rate limiting (10 calls/60s)
- ✅ Password hashing
- ✅ Session management
- ✅ Environment variable validation

## Maintenance

### Regular Tasks
- Database optimization (monthly)
- Cache clearing (as needed)
- Log rotation (weekly)
- Backup verification (daily)

### Monitoring
- Check performance metrics
- Review error logs
- Monitor database size
- Track user activity

---

**For more details, see the specific documentation files in the `docs/` directory.**
