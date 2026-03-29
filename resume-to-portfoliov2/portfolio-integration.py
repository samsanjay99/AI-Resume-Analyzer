"""
Portfolio Integration Module
Integrates the modern portfolio template with the resume analysis system
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

class PortfolioGenerator:
    """
    Generates modern tech portfolios from resume data
    """
    
    def __init__(self, template_dir: str = "resume-to-portfoliov2"):
        self.template_dir = Path(template_dir)
        self.output_dir = Path("generated_portfolios")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_template_files(self) -> Dict[str, str]:
        """Load template files (HTML, CSS, JS)"""
        template_files = {}
        
        # Load HTML template
        html_path = self.template_dir / "index.html"
        if html_path.exists():
            with open(html_path, 'r', encoding='utf-8') as f:
                template_files['html'] = f.read()
        
        # Load CSS
        css_path = self.template_dir / "main.css"
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                template_files['css'] = f.read()
        
        # Load JavaScript
        js_path = self.template_dir / "assets" / "js" / "main.js"
        if js_path.exists():
            with open(js_path, 'r', encoding='utf-8') as f:
                template_files['js'] = f.read()
        
        return template_files
    
    def extract_skills_by_category(self, skills_list: list) -> Dict[str, list]:
        """Categorize skills into different technology groups"""
        
        # Define skill categories
        categories = {
            'programming_languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 
                'go', 'rust', 'typescript', 'swift', 'kotlin', 'scala', 'r'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 
                'flask', 'spring', 'laravel', 'rails', 'asp.net', 'next.js',
                'nuxt.js', 'svelte', 'fastapi', 'nestjs'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 
                'oracle', 'cassandra', 'elasticsearch', 'dynamodb', 'firebase'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 
                'git', 'github', 'gitlab', 'terraform', 'ansible', 'nginx'
            ]
        }
        
        # Categorize skills
        categorized = {category: [] for category in categories.keys()}
        
        for skill in skills_list:
            skill_lower = skill.lower().strip()
            categorized_flag = False
            
            for category, keywords in categories.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            # If not categorized, add to programming languages as default
            if not categorized_flag:
                categorized['programming_languages'].append(skill)
        
        return categorized
    
    def generate_skill_html(self, skills: list, category: str) -> str:
        """Generate HTML for skill items"""
        if not skills:
            return ""
        
        # Icon mapping for different skills
        icon_map = {
            'javascript': 'fab fa-js-square',
            'python': 'fab fa-python',
            'java': 'fab fa-java',
            'react': 'fab fa-react',
            'angular': 'fab fa-angular',
            'vue': 'fab fa-vuejs',
            'node.js': 'fab fa-node-js',
            'docker': 'fab fa-docker',
            'aws': 'fab fa-aws',
            'git': 'fab fa-git-alt',
            'github': 'fab fa-github',
        }
        
        html_items = []
        for skill in skills:
            skill_key = skill.lower().replace('.', '').replace(' ', '')
            icon = icon_map.get(skill_key, 'fas fa-code')
            
            html_items.append(f'''
            <div class="skill-item">
                <div class="skill-icon">
                    <i class="{icon}"></i>
                </div>
                <div class="skill-name">{skill}</div>
            </div>
            ''')
        
        return ''.join(html_items)
    
    def generate_experience_html(self, experiences: list) -> str:
        """Generate HTML for work experience timeline"""
        if not experiences:
            return '''
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">Your Position</h3>
                    <h4 class="timeline-company">Your Company</h4>
                    <p class="timeline-description">Add your work experience details here</p>
                </div>
                <div class="timeline-date">Start - End</div>
            </div>
            '''
        
        html_items = []
        for exp in experiences:
            html_items.append(f'''
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">{exp.get('position', 'Position')}</h3>
                    <h4 class="timeline-company">{exp.get('company', 'Company')}</h4>
                    <p class="timeline-description">{exp.get('description', 'Job description and key achievements')}</p>
                </div>
                <div class="timeline-date">{exp.get('start_date', 'Start')} - {exp.get('end_date', 'End')}</div>
            </div>
            ''')
        
        return ''.join(html_items)
    
    def generate_education_html(self, education: list) -> str:
        """Generate HTML for education timeline"""
        if not education:
            return '''
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">Your Degree</h3>
                    <h4 class="timeline-company">Your Institution</h4>
                    <p class="timeline-description">Add your educational background</p>
                </div>
                <div class="timeline-date">Year</div>
            </div>
            '''
        
        html_items = []
        for edu in education:
            html_items.append(f'''
            <div class="timeline-item">
                <div class="timeline-content">
                    <h3 class="timeline-title">{edu.get('degree', 'Degree')}</h3>
                    <h4 class="timeline-company">{edu.get('institution', 'Institution')}</h4>
                    <p class="timeline-description">{edu.get('description', 'Relevant coursework and achievements')}</p>
                </div>
                <div class="timeline-date">{edu.get('year', 'Year')}</div>
            </div>
            ''')
        
        return ''.join(html_items)
    
    def generate_projects_html(self, projects: list) -> str:
        """Generate HTML for project cards"""
        if not projects:
            return '''
            <div class="project-card">
                <div class="project-image">
                    <i class="fas fa-laptop-code"></i>
                </div>
                <div class="project-content">
                    <h3 class="project-title">Sample Project</h3>
                    <p class="project-description">A brief description of your project and its key features.</p>
                    <div class="project-tech">
                        <span class="tech-tag">Technology 1</span>
                        <span class="tech-tag">Technology 2</span>
                    </div>
                    <div class="project-links">
                        <a href="#" class="project-link">
                            <i class="fas fa-external-link-alt"></i> Live Demo
                        </a>
                        <a href="#" class="project-link">
                            <i class="fab fa-github"></i> Source Code
                        </a>
                    </div>
                </div>
            </div>
            '''
        
        html_items = []
        for project in projects:
            # Generate tech tags
            tech_tags = ''
            if 'technologies' in project and project['technologies']:
                tech_tags = ''.join([f'<span class="tech-tag">{tech}</span>' 
                                   for tech in project['technologies']])
            
            # Generate project links
            links = []
            if project.get('live_url'):
                links.append(f'''
                <a href="{project['live_url']}" class="project-link" target="_blank">
                    <i class="fas fa-external-link-alt"></i> Live Demo
                </a>
                ''')
            
            if project.get('github_url'):
                links.append(f'''
                <a href="{project['github_url']}" class="project-link" target="_blank">
                    <i class="fab fa-github"></i> Source Code
                </a>
                ''')
            
            project_links = ''.join(links)
            
            html_items.append(f'''
            <div class="project-card">
                <div class="project-image">
                    <i class="fas fa-laptop-code"></i>
                </div>
                <div class="project-content">
                    <h3 class="project-title">{project.get('name', 'Project Name')}</h3>
                    <p class="project-description">{project.get('description', 'Project description')}</p>
                    <div class="project-tech">
                        {tech_tags}
                    </div>
                    <div class="project-links">
                        {project_links}
                    </div>
                </div>
            </div>
            ''')
        
        return ''.join(html_items)
    
    def populate_template(self, template_html: str, resume_data: Dict[str, Any]) -> str:
        """Populate HTML template with resume data"""
        
        # Extract personal information
        personal_info = resume_data.get('personal_info', {})
        full_name = personal_info.get('name', 'Your Name')
        first_name = full_name.split()[0] if full_name else 'Your'
        
        # Extract professional information
        professional_summary = resume_data.get('summary', 'Passionate developer with expertise in modern technologies.')
        
        # Extract and categorize skills
        skills_list = resume_data.get('skills', [])
        categorized_skills = self.extract_skills_by_category(skills_list)
        
        # Calculate statistics
        years_exp = len(resume_data.get('experience', [])) * 2  # Rough estimate
        project_count = len(resume_data.get('projects', [])) + 10  # Add some buffer
        skill_count = len(skills_list)
        
        # Generate HTML sections
        programming_languages_html = self.generate_skill_html(
            categorized_skills['programming_languages'], 'programming'
        )
        frameworks_html = self.generate_skill_html(
            categorized_skills['frameworks'], 'frameworks'
        )
        databases_html = self.generate_skill_html(
            categorized_skills['databases'], 'databases'
        )
        cloud_devops_html = self.generate_skill_html(
            categorized_skills['cloud_devops'], 'cloud'
        )
        
        experience_html = self.generate_experience_html(resume_data.get('experience', []))
        education_html = self.generate_education_html(resume_data.get('education', []))
        projects_html = self.generate_projects_html(resume_data.get('projects', []))
        
        # Define all replacements
        replacements = {
            '{{FULL_NAME}}': full_name,
            '{{FIRST_NAME}}': first_name,
            '{{EMAIL}}': personal_info.get('email', 'your.email@example.com'),
            '{{PHONE}}': personal_info.get('phone', '+1 (555) 123-4567'),
            '{{LOCATION}}': personal_info.get('location', 'Your City, Country'),
            '{{LINKEDIN_URL}}': personal_info.get('linkedin', 'https://linkedin.com/in/yourprofile'),
            '{{GITHUB_URL}}': personal_info.get('github', 'https://github.com/yourusername'),
            '{{TWITTER_URL}}': personal_info.get('twitter', 'https://twitter.com/yourusername'),
            '{{RESUME_DOWNLOAD_LINK}}': './assets/resume.pdf',
            
            '{{JOB_TITLE}}': resume_data.get('current_role', 'Software Developer'),
            '{{CURRENT_POSITION}}': resume_data.get('current_role', 'Software Developer'),
            '{{PROFESSIONAL_SUMMARY}}': professional_summary,
            '{{ABOUT_DESCRIPTION}}': professional_summary,
            '{{CONTACT_MESSAGE}}': "I'm always interested in new opportunities and exciting projects. Let's connect!",
            
            '{{YEARS_EXPERIENCE}}': str(max(years_exp, 1)),
            '{{PROJECT_COUNT}}': str(max(project_count, 5)),
            '{{SKILL_COUNT}}': str(max(skill_count, 10)),
            
            '{{EDUCATION_DEGREE}}': resume_data.get('education', [{}])[0].get('degree', "Bachelor's Degree") if resume_data.get('education') else "Bachelor's Degree",
            
            '{{PRIMARY_SKILLS}}': ', '.join(skills_list[:5]) if skills_list else 'JavaScript, Python, React, Node.js',
            '{{PROGRAMMING_LANGUAGES}}': programming_languages_html,
            '{{FRAMEWORKS}}': frameworks_html,
            '{{DATABASES_TOOLS}}': databases_html,
            '{{CLOUD_DEVOPS}}': cloud_devops_html,
            
            '{{WORK_EXPERIENCE}}': experience_html,
            '{{EDUCATION_HISTORY}}': education_html,
            '{{PROJECTS_LIST}}': projects_html,
            
            '{{SECONDARY_TITLE_1}}': 'Full Stack Developer',
            '{{SECONDARY_TITLE_2}}': 'Problem Solver',
            '{{SECONDARY_TITLE_3}}': 'Tech Enthusiast',
        }
        
        # Apply all replacements
        populated_html = template_html
        for placeholder, value in replacements.items():
            populated_html = populated_html.replace(placeholder, value)
        
        return populated_html
    
    def create_portfolio_package(self, resume_data: Dict[str, Any], 
                               output_name: Optional[str] = None) -> str:
        """Create a complete portfolio package as ZIP file"""
        
        if not output_name:
            name = resume_data.get('personal_info', {}).get('name', 'portfolio')
            output_name = name.lower().replace(' ', '_')
        
        # Create temporary directory for portfolio files
        temp_dir = self.output_dir / f"{output_name}_temp"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Load template files
            template_files = self.load_template_files()
            
            # Populate HTML template
            if 'html' in template_files:
                populated_html = self.populate_template(template_files['html'], resume_data)
                
                # Write populated HTML
                with open(temp_dir / 'index.html', 'w', encoding='utf-8') as f:
                    f.write(populated_html)
            
            # Copy CSS file
            if 'css' in template_files:
                with open(temp_dir / 'main.css', 'w', encoding='utf-8') as f:
                    f.write(template_files['css'])
            
            # Create assets directory and copy JS
            assets_dir = temp_dir / 'assets' / 'js'
            assets_dir.mkdir(parents=True, exist_ok=True)
            
            if 'js' in template_files:
                with open(assets_dir / 'main.js', 'w', encoding='utf-8') as f:
                    f.write(template_files['js'])
            
            # Copy any additional assets (images, etc.)
            source_assets = self.template_dir / 'assets'
            if source_assets.exists():
                # Copy images and other assets
                for item in source_assets.rglob('*'):
                    if item.is_file() and not item.name.endswith('.js'):
                        relative_path = item.relative_to(source_assets)
                        dest_path = temp_dir / 'assets' / relative_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
            
            # Create ZIP file
            zip_path = self.output_dir / f"{output_name}_portfolio.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            return str(zip_path)
        
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def generate_portfolio_preview(self, resume_data: Dict[str, Any]) -> str:
        """Generate portfolio HTML for preview (without creating files)"""
        template_files = self.load_template_files()
        
        if 'html' not in template_files:
            raise FileNotFoundError("HTML template not found")
        
        return self.populate_template(template_files['html'], resume_data)


# Example usage function
def generate_portfolio_from_resume_data(resume_data: Dict[str, Any]) -> str:
    """
    Main function to generate portfolio from resume data
    Returns path to generated ZIP file
    """
    generator = PortfolioGenerator()
    zip_path = generator.create_portfolio_package(resume_data)
    return zip_path


# Example resume data for testing
example_resume_data = {
    "personal_info": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe"
    },
    "summary": "Experienced full-stack developer with 5+ years of experience building scalable web applications. Passionate about clean code, user experience, and modern technologies.",
    "current_role": "Senior Full Stack Developer",
    "skills": [
        "JavaScript", "Python", "React", "Node.js", "Express", "MongoDB", 
        "PostgreSQL", "AWS", "Docker", "Git", "TypeScript", "Vue.js"
    ],
    "experience": [
        {
            "position": "Senior Full Stack Developer",
            "company": "Tech Corp",
            "start_date": "2022",
            "end_date": "Present",
            "description": "Led development of scalable web applications serving 100k+ users. Implemented microservices architecture and improved system performance by 40%."
        },
        {
            "position": "Full Stack Developer",
            "company": "StartupXYZ",
            "start_date": "2020",
            "end_date": "2022",
            "description": "Developed and maintained multiple client projects using React, Node.js, and MongoDB. Collaborated with design team to implement responsive UI/UX."
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Technology",
            "year": "2020",
            "description": "Graduated Magna Cum Laude with focus on software engineering and algorithms."
        }
    ],
    "projects": [
        {
            "name": "E-Commerce Platform",
            "description": "Full-featured e-commerce platform with payment integration, inventory management, and admin dashboard.",
            "technologies": ["React", "Node.js", "MongoDB", "Stripe"],
            "live_url": "https://example-ecommerce.com",
            "github_url": "https://github.com/johndoe/ecommerce"
        },
        {
            "name": "Task Management App",
            "description": "Collaborative task management application with real-time updates and team collaboration features.",
            "technologies": ["Vue.js", "Express", "Socket.io", "PostgreSQL"],
            "live_url": "https://example-tasks.com",
            "github_url": "https://github.com/johndoe/taskapp"
        }
    ]
}


if __name__ == "__main__":
    # Test the portfolio generation
    generator = PortfolioGenerator()
    zip_path = generator.create_portfolio_package(example_resume_data, "john_doe")
    print(f"Portfolio generated: {zip_path}")