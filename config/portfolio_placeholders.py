"""
Portfolio Placeholders Configuration
====================================

This file contains all the placeholders used in the portfolio template.
You can easily modify the default values here, and they will be used
when generating portfolios if the corresponding data is not found in the resume.

Usage:
1. Fill in your personal information in the PERSONAL_DATA section
2. Customize the default values in the DEFAULT_DATA section
3. The system will automatically use your data when available, 
   falling back to defaults when needed
"""

# =============================================================================
# PERSONAL DATA - Fill this with your actual information
# =============================================================================

PERSONAL_DATA = {
    # Basic Information
    "FULL_NAME": "Your Full Name",
    "FIRST_NAME": "Your",  # Will be auto-extracted from FULL_NAME if not provided
    "EMAIL": "your.email@example.com",
    "PHONE": "+1 (555) 123-4567",
    "LOCATION": "Your City, Country",
    
    # Professional Information
    "JOB_TITLE": "Your Job Title",
    "CURRENT_POSITION": "Your Current Position",
    "PROFESSIONAL_SUMMARY": "Your professional summary goes here. Describe your expertise, passion, and what makes you unique in your field.",
    "ABOUT_DESCRIPTION": "Tell your story here. What drives you? What are your goals? What makes you passionate about your work?",
    
    # Contact & Social Links
    "LINKEDIN_URL": "https://linkedin.com/in/yourprofile",
    "GITHUB_URL": "https://github.com/yourusername",
    "TWITTER_URL": "https://twitter.com/yourusername",
    "RESUME_DOWNLOAD_LINK": "#",  # Link to your resume file
    
    # Statistics
    "YEARS_EXPERIENCE": "3",
    "PROJECT_COUNT": "10",
    "SKILL_COUNT": "15",
    
    # Education
    "EDUCATION_DEGREE": "Your Degree",
    
    # Contact Message
    "CONTACT_MESSAGE": "I'm always interested in new opportunities and collaborations. Let's connect and discuss how we can work together!",
    
    # Skills (comma-separated for PRIMARY_SKILLS)
    "PRIMARY_SKILLS": "Python, JavaScript, React, Node.js",
    
    # Typewriter Effect Titles
    "SECONDARY_TITLE_1": "Problem Solver",
    "SECONDARY_TITLE_2": "Creative Thinker", 
    "SECONDARY_TITLE_3": "Team Player",
}

# =============================================================================
# DEFAULT DATA - These are fallback values when resume data is not available
# =============================================================================

DEFAULT_DATA = {
    # Basic Information Defaults
    "FULL_NAME": "Professional Developer",
    "FIRST_NAME": "Professional",
    "EMAIL": "contact@example.com",
    "PHONE": "+91 9900586091",
    "LOCATION": "Available Worldwide",
    
    # Professional Defaults
    "JOB_TITLE": "Software Developer",
    "CURRENT_POSITION": "Software Developer",
    "PROFESSIONAL_SUMMARY": "Passionate software developer with expertise in modern technologies. Dedicated to creating innovative solutions and delivering high-quality code.",
    "ABOUT_DESCRIPTION": "I'm a dedicated professional who loves solving complex problems through technology. With a passion for continuous learning and innovation, I strive to create meaningful solutions that make a difference.",
    
    # Social Links Defaults
    "LINKEDIN_URL": "https://linkedin.com",
    "GITHUB_URL": "https://github.com",
    "TWITTER_URL": "https://twitter.com",
    "RESUME_DOWNLOAD_LINK": "#",
    
    # Statistics Defaults
    "YEARS_EXPERIENCE": "2",
    "PROJECT_COUNT": "5",
    "SKILL_COUNT": "10",
    
    # Education Default
    "EDUCATION_DEGREE": "Computer Science Degree",
    
    # Contact Message Default
    "CONTACT_MESSAGE": "I'm always open to discussing new opportunities and interesting projects. Feel free to reach out!",
    
    # Skills Default
    "PRIMARY_SKILLS": "Programming, Problem Solving, Team Work",
    
    # Typewriter Defaults
    "SECONDARY_TITLE_1": "Code Enthusiast",
    "SECONDARY_TITLE_2": "Innovation Driver",
    "SECONDARY_TITLE_3": "Solution Builder",
}

# =============================================================================
# SKILLS SECTIONS - Organize your skills by category
# =============================================================================

SKILLS_DATA = {
    "PROGRAMMING_LANGUAGES": [
        {"name": "Python", "level": "Advanced"},
        {"name": "JavaScript", "level": "Advanced"},
        {"name": "Java", "level": "Intermediate"},
        {"name": "C++", "level": "Intermediate"},
        {"name": "TypeScript", "level": "Intermediate"},
        {"name": "SQL", "level": "Advanced"},
    ],
    
    "FRAMEWORKS": [
        {"name": "React", "level": "Advanced"},
        {"name": "Node.js", "level": "Advanced"},
        {"name": "Django", "level": "Intermediate"},
        {"name": "Flask", "level": "Intermediate"},
        {"name": "Express.js", "level": "Advanced"},
        {"name": "Vue.js", "level": "Beginner"},
    ],
    
    "DATABASES_TOOLS": [
        {"name": "PostgreSQL", "level": "Advanced"},
        {"name": "MongoDB", "level": "Intermediate"},
        {"name": "Redis", "level": "Intermediate"},
        {"name": "MySQL", "level": "Advanced"},
        {"name": "Git", "level": "Advanced"},
        {"name": "Docker", "level": "Intermediate"},
    ],
    
    "CLOUD_DEVOPS": [
        {"name": "AWS", "level": "Intermediate"},
        {"name": "Google Cloud", "level": "Beginner"},
        {"name": "Docker", "level": "Intermediate"},
        {"name": "Kubernetes", "level": "Beginner"},
        {"name": "CI/CD", "level": "Intermediate"},
        {"name": "Linux", "level": "Advanced"},
    ],
}

# =============================================================================
# EXPERIENCE DATA - Your work experience
# =============================================================================

EXPERIENCE_DATA = [
    {
        "title": "Senior Software Developer",
        "company": "Tech Company Inc.",
        "duration": "2022 - Present",
        "description": "Led development of scalable web applications using modern technologies. Collaborated with cross-functional teams to deliver high-quality software solutions.",
        "achievements": [
            "Improved application performance by 40%",
            "Led a team of 5 developers",
            "Implemented CI/CD pipelines"
        ]
    },
    {
        "title": "Software Developer",
        "company": "StartUp Solutions",
        "duration": "2020 - 2022",
        "description": "Developed and maintained web applications using React and Node.js. Worked closely with designers and product managers to create user-friendly interfaces.",
        "achievements": [
            "Built 3 major features from scratch",
            "Reduced bug reports by 30%",
            "Mentored junior developers"
        ]
    },
    {
        "title": "Junior Developer",
        "company": "Code Academy",
        "duration": "2019 - 2020",
        "description": "Started career as a junior developer, learning best practices and contributing to various projects. Gained experience in full-stack development.",
        "achievements": [
            "Completed 10+ projects successfully",
            "Learned 5 new technologies",
            "Received excellent performance reviews"
        ]
    }
]

# =============================================================================
# EDUCATION DATA - Your educational background
# =============================================================================

EDUCATION_DATA = [
    {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "University of Technology",
        "duration": "2015 - 2019",
        "description": "Focused on software engineering, algorithms, and data structures. Graduated with honors.",
        "achievements": [
            "Graduated Magna Cum Laude",
            "President of Computer Science Club",
            "Dean's List for 6 semesters"
        ]
    },
    {
        "degree": "High School Diploma",
        "institution": "Central High School",
        "duration": "2011 - 2015",
        "description": "Completed high school with focus on mathematics and science.",
        "achievements": [
            "Valedictorian",
            "National Honor Society",
            "Math Competition Winner"
        ]
    }
]

# =============================================================================
# PROJECTS DATA - Your portfolio projects
# =============================================================================

PROJECTS_DATA = [
    {
        "title": "E-Commerce Platform",
        "description": "A full-stack e-commerce solution built with React, Node.js, and PostgreSQL. Features include user authentication, payment processing, and admin dashboard.",
        "technologies": ["React", "Node.js", "PostgreSQL", "Stripe API"],
        "github_url": "https://github.com/yourusername/ecommerce-platform",
        "live_url": "https://your-ecommerce-demo.com",
        "image_url": "assets/img/project1.jpg",
        "featured": True
    },
    {
        "title": "Task Management App",
        "description": "A collaborative task management application with real-time updates, drag-and-drop functionality, and team collaboration features.",
        "technologies": ["Vue.js", "Express.js", "MongoDB", "Socket.io"],
        "github_url": "https://github.com/yourusername/task-manager",
        "live_url": "https://your-taskmanager-demo.com",
        "image_url": "assets/img/project2.jpg",
        "featured": True
    },
    {
        "title": "Weather Dashboard",
        "description": "A responsive weather dashboard that displays current weather and forecasts for multiple cities using external APIs.",
        "technologies": ["JavaScript", "HTML5", "CSS3", "Weather API"],
        "github_url": "https://github.com/yourusername/weather-dashboard",
        "live_url": "https://your-weather-demo.com",
        "image_url": "assets/img/project3.jpg",
        "featured": False
    },
    {
        "title": "Portfolio Website",
        "description": "A personal portfolio website showcasing projects, skills, and experience. Built with modern web technologies and responsive design.",
        "technologies": ["HTML5", "CSS3", "JavaScript", "SCSS"],
        "github_url": "https://github.com/yourusername/portfolio",
        "live_url": "https://your-portfolio.com",
        "image_url": "assets/img/project4.jpg",
        "featured": False
    }
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_placeholder_value(key, extracted_data=None, use_personal_data=True):
    """
    Get the value for a placeholder key.
    Priority: extracted_data > PERSONAL_DATA > DEFAULT_DATA
    
    Args:
        key: The placeholder key (e.g., 'FULL_NAME')
        extracted_data: Data extracted from resume
        use_personal_data: Whether to use PERSONAL_DATA or go straight to defaults
    
    Returns:
        The value to use for the placeholder
    """
    # First try extracted data
    if extracted_data and key in extracted_data:
        value = extracted_data[key]
        if value and str(value).strip():
            return str(value).strip()
    
    # Then try personal data if enabled
    if use_personal_data and key in PERSONAL_DATA:
        value = PERSONAL_DATA[key]
        if value and str(value).strip() and str(value).strip() not in ['Your Full Name', 'Your Job Title', 'your.email@example.com']:
            return str(value).strip()
    
    # Finally use default data
    if key in DEFAULT_DATA:
        return DEFAULT_DATA[key]
    
    # Fallback
    return f"[{key}]"

def get_first_name(full_name):
    """Extract first name from full name"""
    if not full_name or full_name.strip() in ['Your Full Name', 'Professional Developer']:
        return DEFAULT_DATA.get('FIRST_NAME', 'Professional')
    
    parts = full_name.strip().split()
    return parts[0] if parts else DEFAULT_DATA.get('FIRST_NAME', 'Professional')

def generate_skills_html(skills_data, category):
    """Generate HTML for skills section"""
    if category not in skills_data:
        return '<div class="skill-item">No skills available</div>'
    
    skills = skills_data[category]
    html_parts = []
    
    for skill in skills:
        if isinstance(skill, dict):
            name = skill.get('name', 'Unknown Skill')
            level = skill.get('level', 'Beginner')
            html_parts.append(f'''
                <div class="skill-item">
                    <div class="skill-name">{name}</div>
                    <div class="skill-level">{level}</div>
                </div>
            ''')
        else:
            html_parts.append(f'''
                <div class="skill-item">
                    <div class="skill-name">{skill}</div>
                </div>
            ''')
    
    return '\n'.join(html_parts)

def generate_experience_html(experience_data):
    """Generate HTML for experience section"""
    if not experience_data:
        return '<div class="timeline-item">No experience data available</div>'
    
    html_parts = []
    for exp in experience_data:
        html_parts.append(f'''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h3 class="timeline-title">{exp.get('title', 'Position')}</h3>
                    <h4 class="timeline-company">{exp.get('company', 'Company')}</h4>
                    <span class="timeline-date">{exp.get('duration', 'Duration')}</span>
                    <p class="timeline-description">{exp.get('description', 'Description')}</p>
                    <ul class="timeline-achievements">
                        {''.join([f'<li>{achievement}</li>' for achievement in exp.get('achievements', [])])}
                    </ul>
                </div>
            </div>
        ''')
    
    return '\n'.join(html_parts)

def generate_education_html(education_data):
    """Generate HTML for education section"""
    if not education_data:
        return '<div class="timeline-item">No education data available</div>'
    
    html_parts = []
    for edu in education_data:
        html_parts.append(f'''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h3 class="timeline-title">{edu.get('degree', 'Degree')}</h3>
                    <h4 class="timeline-institution">{edu.get('institution', 'Institution')}</h4>
                    <span class="timeline-date">{edu.get('duration', 'Duration')}</span>
                    <p class="timeline-description">{edu.get('description', 'Description')}</p>
                    <ul class="timeline-achievements">
                        {''.join([f'<li>{achievement}</li>' for achievement in edu.get('achievements', [])])}
                    </ul>
                </div>
            </div>
        ''')
    
    return '\n'.join(html_parts)

def generate_projects_html(projects_data):
    """Generate HTML for projects section"""
    if not projects_data:
        return '<div class="project-card">No projects available</div>'
    
    html_parts = []
    for project in projects_data:
        featured_class = 'featured' if project.get('featured', False) else ''
        technologies = ', '.join(project.get('technologies', []))
        
        html_parts.append(f'''
            <div class="project-card {featured_class}">
                <div class="project-image">
                    <img src="{project.get('image_url', 'assets/img/project-placeholder.jpg')}" alt="{project.get('title', 'Project')}">
                    <div class="project-overlay">
                        <div class="project-links">
                            <a href="{project.get('github_url', '#')}" class="project-link" target="_blank">
                                <i class="fab fa-github"></i>
                            </a>
                            <a href="{project.get('live_url', '#')}" class="project-link" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="project-content">
                    <h3 class="project-title">{project.get('title', 'Project Title')}</h3>
                    <p class="project-description">{project.get('description', 'Project description')}</p>
                    <div class="project-technologies">
                        <span class="tech-label">Technologies:</span>
                        <span class="tech-list">{technologies}</span>
                    </div>
                </div>
            </div>
        ''')
    
    return '\n'.join(html_parts)

# =============================================================================
# MAIN PLACEHOLDER MAPPING
# =============================================================================

def get_all_placeholders(extracted_data=None, use_personal_data=True):
    """
    Get all placeholder values for the portfolio template.
    
    Args:
        extracted_data: Data extracted from resume
        use_personal_data: Whether to use PERSONAL_DATA
    
    Returns:
        Dictionary with all placeholder values
    """
    # Get basic placeholder values
    placeholders = {}
    
    # All basic placeholders
    basic_keys = [
        'FULL_NAME', 'EMAIL', 'PHONE', 'LOCATION', 'JOB_TITLE', 
        'CURRENT_POSITION', 'PROFESSIONAL_SUMMARY', 'ABOUT_DESCRIPTION',
        'LINKEDIN_URL', 'GITHUB_URL', 'TWITTER_URL', 'RESUME_DOWNLOAD_LINK',
        'YEARS_EXPERIENCE', 'PROJECT_COUNT', 'SKILL_COUNT', 'EDUCATION_DEGREE',
        'CONTACT_MESSAGE', 'PRIMARY_SKILLS', 'SECONDARY_TITLE_1', 
        'SECONDARY_TITLE_2', 'SECONDARY_TITLE_3'
    ]
    
    for key in basic_keys:
        placeholders[key] = get_placeholder_value(key, extracted_data, use_personal_data)
    
    # Generate FIRST_NAME from FULL_NAME
    placeholders['FIRST_NAME'] = get_first_name(placeholders['FULL_NAME'])
    
    # Generate complex HTML sections
    placeholders['PROGRAMMING_LANGUAGES'] = generate_skills_html(SKILLS_DATA, 'PROGRAMMING_LANGUAGES')
    placeholders['FRAMEWORKS'] = generate_skills_html(SKILLS_DATA, 'FRAMEWORKS')
    placeholders['DATABASES_TOOLS'] = generate_skills_html(SKILLS_DATA, 'DATABASES_TOOLS')
    placeholders['CLOUD_DEVOPS'] = generate_skills_html(SKILLS_DATA, 'CLOUD_DEVOPS')
    
    placeholders['WORK_EXPERIENCE'] = generate_experience_html(EXPERIENCE_DATA)
    placeholders['EDUCATION_HISTORY'] = generate_education_html(EDUCATION_DATA)
    placeholders['PROJECTS_LIST'] = generate_projects_html(PROJECTS_DATA)
    
    return placeholders

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Portfolio Placeholders Configuration")
    print("=" * 50)
    
    # Get all placeholders with personal data
    placeholders = get_all_placeholders(use_personal_data=True)
    
    print(f"Full Name: {placeholders['FULL_NAME']}")
    print(f"Job Title: {placeholders['JOB_TITLE']}")
    print(f"Email: {placeholders['EMAIL']}")
    print(f"First Name: {placeholders['FIRST_NAME']}")
    
    print("\nTo customize your portfolio:")
    print("1. Edit the PERSONAL_DATA section with your information")
    print("2. Update SKILLS_DATA, EXPERIENCE_DATA, EDUCATION_DATA, and PROJECTS_DATA")
    print("3. The portfolio generator will automatically use your data")